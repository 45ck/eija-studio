"""Formal evidence in the application layer: seal what an adapter collected, and build the packet view.

The adapter (behind the ``FormalEvidenceSource`` port) only reads tool reports; the kernel (``domain.evidence``)
recomputes every verdict. Nothing here reads a status label from an artifact.
"""
from __future__ import annotations

from typing import Any, Callable

from eija_studio.domain.evidence import FormalVerdict, TECHNICAL_DIMENSIONS, aggregate_formal, intact_artifact
from eija_studio.domain.evidence_kinds import KINDS
from eija_studio.domain.formal import FORMAL_PRODUCER, PASS, Context, FormalArtifact, KindSpec
from eija_studio.domain.models import Workflow, fingerprint
from eija_studio.domain.pack import Pack
from eija_studio.domain.policy import what_if
from .ports import FormalEvidenceSource

BLOCKING = ("FAIL", "CONFLICT")  # a counterexample stops approval; UNKNOWN, NOT_RUN and STALE never do, and are never green


def attach(source: FormalEvidenceSource | None, baseline: Workflow, candidate: Workflow, subject: dict[str, Any],
          existing: list[dict[str, Any]], seal: Callable[[dict[str, Any]], dict[str, Any]], stamp: str,
          new_id: Callable[[], str], pack: Pack | None = None) -> list[dict[str, Any]]:
    """Sealed receipts for every registered kind the source returned, skipping an exact repeat of the latest one.
    With a ``pack``, a kind the pack does not verify from the checkout's reports is NOT_RUN with the pack's reason."""
    receipts: list[dict[str, Any]] = []
    for item in for_pack(_collected(source, baseline, candidate), pack):
        spec = KINDS.get(item.kind)
        if spec is None:
            continue  # the kernel has no admissibility rule for it, so it could only ever be UNKNOWN
        receipt = {"id": new_id(), "claim": spec.claim, "kind": spec.kind, "subject": subject, "producer": FORMAL_PRODUCER,
                   "method": spec.method, "created_at": stamp, "artifact_hash": fingerprint(item.artifact),
                   "artifact": item.artifact, "measurements": item.measurements}
        if not _repeat(receipt, [*existing, *receipts]):
            receipts.append(seal(receipt))
    return receipts


def _collected(source: FormalEvidenceSource | None, baseline: Workflow, candidate: Workflow) -> list[FormalArtifact]:
    """The source's artifacts. An optional evidence source that fails must not block runtime verification: every kind is
    then NOT_RUN with the reason (never absent, never a pass)."""
    if source is None:
        return []
    try:
        return source.collect(baseline, candidate)
    except Exception as error:  # adapter boundary: any failure of an optional source is reported, not raised
        reason = f"the formal evidence source failed ({type(error).__name__}); no formal evidence was collected"
        return [FormalArtifact(k, {"protocol": s.protocol, "not_run": {"reason": reason, "prerequisite": "a working formal evidence source"}}, {})
                for k, s in KINDS.items()]


# Verifier modes whose evidence the checkout's committed formal reports describe. Any other mode (generated, not_run)
# or an undeclared kind means those reports are about some other pack's model, so they must not count for this one.
READS_REPORTS = ("kernel", "hand_encoded")


def pack_not_run(pack: Pack, kind: str) -> str | None:
    """Why ``kind`` is NOT_RUN for ``pack`` (None when the pack verifies it from the checkout's reports)."""
    verifier = pack.verifier(kind)
    if verifier is None:
        return f"the pack {pack.id} declares no {kind} verifier"
    if verifier.mode in READS_REPORTS:
        return None
    return verifier.reason or f"the pack {pack.id} does not produce {kind} evidence ({verifier.mode})"


def for_pack(items: list[FormalArtifact], pack: Pack | None) -> list[FormalArtifact]:
    """Artifacts of a kind this pack does not verify from the reports become one NOT_RUN artifact with the pack's reason."""
    if pack is None:
        return items
    out, replaced = [], set()
    for item in items:
        reason = pack_not_run(pack, item.kind)
        if reason is None:
            out.append(item)
        elif item.kind not in replaced:
            replaced.add(item.kind)
            protocol = KINDS[item.kind].protocol if item.kind in KINDS else str(item.artifact.get("protocol", ""))
            out.append(FormalArtifact(item.kind, {"protocol": protocol, "not_run": {
                "reason": reason, "prerequisite": f"a {item.kind} verifier for the pack {pack.id}"}}, {}))
    return out


def verifier_view(pack: Pack) -> list[dict[str, str]]:
    """Every verifier the pack declares, with the status its mode implies before any evidence is read: a kind that is not
    produced for this pack (``not_run``) is NOT_RUN with the reason, never absent and never a pass."""
    status = {"not_run": "NOT_RUN", "generated": "NOT_RUN"}
    return [{"kind": v.kind, "mode": v.mode, "status": status.get(v.mode, "FROM_EVIDENCE"), "reason": v.reason}
            for v in pack.verifiers]


def _repeat(receipt: dict[str, Any], others: list[dict[str, Any]]) -> bool:
    same_kind = [r for r in others if r.get("kind") == receipt["kind"]]
    latest = same_kind[-1] if same_kind else None
    return latest is not None and latest.get("artifact_hash") == receipt["artifact_hash"] and all(
        latest.get("subject", {}).get(k) == receipt["subject"].get(k) for k in TECHNICAL_DIMENSIONS)


def _details(spec: KindSpec, verdict: FormalVerdict, authenticator: Callable[[dict[str, Any]], bool]) -> dict[str, Any]:
    """What the deciding artifact carries (tool, bounds, assumptions, counterexamples), only where it was admitted or refuted
    and the receipt is authentic and hash-consistent (tampered bytes are never displayed as if they were evidence)."""
    artifact = None if verdict.receipt is None else intact_artifact(verdict.receipt, spec.kind, authenticator)
    if artifact is None or verdict.status not in (PASS, *BLOCKING):
        return {}
    try:
        return spec.describe(artifact)
    except (KeyError, TypeError, AttributeError, IndexError):
        return {"details_unavailable": "the artifact could not be summarised"}


def _entry(spec: KindSpec, verdict: FormalVerdict, authenticator: Callable[[dict[str, Any]], bool]) -> dict[str, Any]:
    return {"kind": spec.kind, "claim": spec.claim, "status": verdict.status, "evidence_level": spec.level,
            "receipts": verdict.receipts, "receipt_id": None if verdict.receipt is None else verdict.receipt.get("id"),
            "reasons": list(verdict.reasons), "establishes": spec.establishes,
            "does_not_establish": list(spec.does_not_establish), "prerequisites": spec.prerequisites} | _details(spec, verdict, authenticator)


def _explanations(receipts: list[dict[str, Any]], authenticator: Callable[[dict[str, Any]], bool],
                  verdicts: dict[str, FormalVerdict], policy_errors: tuple[str, ...]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for spec in KINDS.values():
        for receipt in receipts:
            artifact = intact_artifact(receipt, spec.kind, authenticator)
            found += [x | {"positive_proof": verdicts[spec.kind].status, "receipt_id": receipt.get("id")}
                      for x in ([] if artifact is None else spec.explain(artifact, policy_errors))]
    seen: set[tuple[str, str]] = set()
    unique = []
    for x in found:  # the same control can appear in several receipts of one kind
        key = (str(x.get("source")), str(x.get("control")))
        if key not in seen:
            seen.add(key)
            unique.append(x)
    return unique


def packet_view(receipts: list[dict[str, Any]], subject: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],
                context: Context, policy_errors: list[str], pack: Pack | None = None) -> dict[str, Any]:
    """The formal part of the review packet: per-kind claims, blockers, the full evidence list, explanations, and (with a
    pack) the pack's declared verifiers, so a kind no registered evidence covers (a TLC check) is shown NOT_RUN too."""
    verdicts = {k: aggregate_formal(k, receipts, subject, authenticator, context) for k in KINDS}
    return {"verifiers": [] if pack is None else verifier_view(pack),
            "claims": {f"formal_{k}": v.status for k, v in verdicts.items()},
            "blockers": [f"FORMAL_EVIDENCE_{v.status}:{k}" for k, v in verdicts.items() if v.status in BLOCKING],
            "evidence": [_entry(KINDS[k], v, authenticator) for k, v in verdicts.items()],
            "explanations": _explanations(receipts, authenticator, verdicts, tuple(policy_errors)) if policy_errors else []}


# What an interpretation the policy refuses would MEAN in the model: the unsupported pack meaning's own transactions,
# applied structurally. A what-if model is evaluated by the kernel's own policy and explained by the formal negative
# controls; it is never a candidate.
def what_if_model(baseline: Workflow, interpretation: str, pack: Pack | None = None) -> Workflow | None:
    """The workflow an unsupported interpretation would produce, or None (supported, unknown, or no transactions)."""
    return what_if(baseline, interpretation, pack)
