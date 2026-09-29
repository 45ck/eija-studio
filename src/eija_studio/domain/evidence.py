"""Compatibility is computed. A supplied green status is never sufficient."""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from typing import Any, Callable
from .evidence_kinds import KINDS
from .formal import FAIL, FORMAL_PRODUCER, NOT_RUN, STALE, UNKNOWN, Assessment, Context, KindSpec, Malformed, not_run_reason
from .models import fingerprint

TECHNICAL_DIMENSIONS = ("semantic", "implementation", "policy", "environment", "harness")
RUNTIME_MATRIX = ("runtime_matrix", "integration_test")


def assess_receipt(receipt: dict[str, Any], subject: dict[str, Any], claim: str, kind: str, context: Context | None = None) -> str:
    if (claim, kind) != RUNTIME_MATRIX:
        # Formal kinds have a registered admissibility rule; anything else is UNKNOWN: this verifier has no authority to establish it.
        return assess_formal_receipt(receipt, subject, claim, kind, context).status
    if receipt.get("claim") != claim or receipt.get("kind") != kind:
        return "UNKNOWN"
    if not isinstance(receipt.get("subject"), dict):
        return "FAIL"
    if any(receipt.get("subject", {}).get(k) != subject.get(k) for k in TECHNICAL_DIMENSIONS):
        return "STALE"
    artifact = receipt.get("artifact")
    if not isinstance(artifact, dict) or fingerprint(artifact) != receipt.get("artifact_hash"):
        return "FAIL"
    if receipt.get("producer") != "eija-local-verifier" or receipt.get("method") != "bounded-runtime-matrix-v1":
        return "UNKNOWN"
    # Never use receipt['status'] as an authority. Recompute from typed observations.
    cells = artifact.get("cells")
    expected = artifact.get("expected_cells")
    if not isinstance(cells, list) or not cells or type(expected) is not int or len(cells) != expected:
        return "FAIL"
    if artifact.get("protocol") != "bounded-runtime-matrix-v1":
        return "UNKNOWN"
    matrix = artifact.get("matrix")
    if not isinstance(matrix, dict) or set(matrix) != {"actors", "states", "actions"}:
        return "FAIL"
    actors = {"teacher-assigned", "teacher-unassigned", "teacher-revoked", "registrar", "viewer"}
    actions = {"Submit", "Recommend", "Approve", "Reject", "Revise"}
    baseline_states = {"Draft", "Submitted", "Approved", "Rejected"}
    if any(not isinstance(v, list) or not all(isinstance(x, str) for x in v) or len(v) != len(set(v)) for v in matrix.values()):
        return "FAIL"
    states = set(matrix["states"])
    if set(matrix["actors"]) != actors or set(matrix["actions"]) != actions or states not in (baseline_states, baseline_states | {"Recommended"}):
        return "FAIL"
    required_keys = set(product(actors, states, actions))
    observed_keys = []
    fields = {"accepted", "state", "version", "audit", "outbox", "operations"}
    for cell in cells:
        if not isinstance(cell, dict) or set(cell) != {"actor", "state", "action", "expected", "actual"}:
            return "FAIL"
        key = (cell["actor"], cell["state"], cell["action"])
        if not all(isinstance(x, str) for x in key):
            return "FAIL"
        observed_keys.append(key)
        for label in ("expected", "actual"):
            observation = cell[label]
            if not isinstance(observation, dict) or set(observation) != fields:
                return "FAIL"
            if type(observation["accepted"]) is not bool or not isinstance(observation["state"], str) or observation["state"] not in states:
                return "FAIL"
            if any(type(observation[k]) is not int or observation[k] not in (0, 1) for k in ("version", "audit", "outbox", "operations")):
                return "FAIL"
    if len(observed_keys) != len(required_keys) or set(observed_keys) != required_keys:
        return "FAIL"
    return "PASS" if all(c["expected"] == c["actual"] for c in cells) else "FAIL"


def combine(statuses: list[str]) -> str:
    """The status algebra: authenticated PASS and FAIL never average (CONFLICT); FAIL beats PASS-less states;
    STALE (a receipt for another subject), then NOT_RUN (a prerequisite was missing), then UNKNOWN."""
    current = [s for s in statuses if s in {"PASS", "FAIL"}]
    if "PASS" in current and "FAIL" in current:
        return "CONFLICT"
    if "FAIL" in current:
        return "FAIL"
    if "PASS" in current:
        return "PASS"
    return next((s for s in (STALE, NOT_RUN) if s in statuses), UNKNOWN)


def aggregate_status(
    receipts: list[dict[str, Any]], subject: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool]
) -> str:
    return combine([assess_receipt(r, subject, "runtime_matrix", "integration_test") if authenticator(r) else "FAIL" for r in receipts])


def assess_formal_receipt(receipt: dict[str, Any], subject: dict[str, Any], claim: str, kind: str,
                          context: Context | None = None) -> Assessment:
    """Per-kind admissibility (ADR-0145): envelope checks in the runtime matrix's order, then the kind's own check.

    A supplied ``status`` label is never read. Structural defects are FAIL, an unknown protocol version is UNKNOWN."""
    spec = KINDS.get(kind)
    if spec is None or spec.claim != claim or receipt.get("claim") != claim or receipt.get("kind") != kind:
        return Assessment(UNKNOWN, ("no admissibility rule is registered for this claim and kind",))
    early = _envelope_problem(receipt, subject, spec)
    if early is not None:
        return early
    return _run_check(spec, receipt["artifact"], context or Context(candidate_semantic=str(subject.get("semantic"))))


def _envelope_problem(receipt: dict[str, Any], subject: dict[str, Any], spec: KindSpec) -> Assessment | None:
    if not isinstance(receipt.get("subject"), dict):
        return Assessment(FAIL, ("the receipt has no subject",))
    if any(receipt["subject"].get(k) != subject.get(k) for k in TECHNICAL_DIMENSIONS):
        return Assessment(STALE, ("the receipt was made for a different technical subject",))
    if not _hash_matches(receipt):
        return Assessment(FAIL, ("the raw artifact does not match its recorded hash",))
    if not _known_producer(receipt, spec):
        return Assessment(UNKNOWN, ("unrecognised producer, method or artifact protocol version",))
    return None


def _run_check(spec: KindSpec, artifact: dict[str, Any], ctx: Context) -> Assessment:
    try:
        return not_run_reason(artifact) if "not_run" in artifact else spec.check(artifact, ctx)
    except Malformed as error:
        return Assessment(FAIL, (f"malformed artifact: {error}",))
    except (KeyError, TypeError, AttributeError, IndexError, ValueError, RecursionError) as error:
        # An artifact is untrusted input: an unforeseen shape must be judged, never crash the packet.
        return Assessment(FAIL, (f"malformed artifact: unexpected {type(error).__name__} while checking",))


def _digest_or_none(artifact: dict[str, Any]) -> str | None:
    try:
        return fingerprint(artifact)
    except (TypeError, ValueError):
        return None  # not canonical JSON: it cannot match any recorded hash


def _hash_matches(receipt: dict[str, Any]) -> bool:
    artifact = receipt.get("artifact")
    return isinstance(artifact, dict) and _digest_or_none(artifact) == receipt.get("artifact_hash")


def _known_producer(receipt: dict[str, Any], spec: KindSpec) -> bool:
    return (receipt.get("producer") == FORMAL_PRODUCER and receipt.get("method") == spec.method
            and receipt["artifact"].get("protocol") == spec.protocol)


def receipt_status(receipt: dict[str, Any], subject: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],
                   context: Context | None = None) -> str:
    """One receipt's applicability by its OWN declared claim and kind; an unauthentic receipt is FAIL."""
    if not authenticator(receipt):
        return FAIL
    return assess_receipt(receipt, subject, str(receipt.get("claim")), str(receipt.get("kind")), context)


def intact_artifact(receipt: dict[str, Any], kind: str, authenticator: Callable[[dict[str, Any]], bool]) -> dict[str, Any] | None:
    """The raw artifact of an authentic, hash-consistent, known-protocol receipt of this kind, whatever its subject.

    For display-only uses (explaining a policy block by a negative control) that must not depend on the
    positive proof being about the current subject; never used to decide a status."""
    spec = KINDS.get(kind)
    if spec is None or not authenticator(receipt) or receipt.get("kind") != kind or receipt.get("claim") != spec.claim:
        return None
    if not _hash_matches(receipt) or not _known_producer(receipt, spec) or "not_run" in receipt["artifact"]:
        return None
    return receipt["artifact"]  # type: ignore[no-any-return]


@dataclass(frozen=True)
class FormalVerdict:
    """The status of one evidence kind for the current subject, with the receipt that decided it."""
    kind: str
    status: str
    receipts: int
    reasons: tuple[str, ...]
    receipt: dict[str, Any] | None


def aggregate_formal(kind: str, receipts: list[dict[str, Any]], subject: dict[str, Any],
                     authenticator: Callable[[dict[str, Any]], bool], context: Context | None = None) -> FormalVerdict:
    """Combine every receipt of one kind. No receipt at all is UNKNOWN: absence is visible, never green."""
    mine = [r for r in receipts if r.get("kind") == kind]
    if not mine:
        return FormalVerdict(kind, UNKNOWN, 0, ("no receipt of this kind is attached to the case",), None)
    assessed = [(r, _assess_authentic(r, subject, authenticator, context)) for r in mine]
    status = combine([a.status for _, a in assessed])
    receipt, assessment = _deciding(assessed, status)
    return FormalVerdict(kind, status, len(assessed), assessment.reasons, receipt)


def _assess_authentic(receipt: dict[str, Any], subject: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],
                      context: Context | None) -> Assessment:
    if not authenticator(receipt):
        return Assessment(FAIL, ("the receipt's local seal does not verify",))
    return assess_formal_receipt(receipt, subject, str(receipt.get("claim")), str(receipt.get("kind")), context)


def _deciding(assessed: list[tuple[dict[str, Any], Assessment]], status: str) -> tuple[dict[str, Any], Assessment]:
    """The receipt that decided the status: the first counterexample, else the latest receipt with that status."""
    wanted = FAIL if status == "CONFLICT" else status
    chosen = [pair for pair in assessed if pair[1].status == wanted]
    return (chosen[0] if wanted == FAIL else chosen[-1]) if chosen else assessed[-1]
