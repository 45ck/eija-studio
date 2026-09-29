"""Formal evidence in the application layer: seal what an adapter collected, and build the packet view.

The adapter (behind the ``FormalEvidenceSource`` port) only reads tool reports; the kernel (``domain.evidence``)
recomputes every verdict. Nothing here reads a status label from an artifact.
"""
from __future__ import annotations

from typing import Any, Callable

from eija_studio.domain.evidence import FormalVerdict, TECHNICAL_DIMENSIONS, aggregate_formal, intact_artifact
from eija_studio.domain.evidence_kinds import KINDS
from eija_studio.domain.formal import FORMAL_PRODUCER, PASS, Context, FormalArtifact, KindSpec
from eija_studio.domain.models import SemanticTransaction, Workflow, fingerprint
from eija_studio.domain.policy import apply_transaction
from .ports import FormalEvidenceSource

BLOCKING = ("FAIL", "CONFLICT")  # a counterexample stops approval; UNKNOWN, NOT_RUN and STALE never do, and are never green


def attach(source: FormalEvidenceSource | None, baseline: Workflow, candidate: Workflow, subject: dict[str, Any],
          existing: list[dict[str, Any]], seal: Callable[[dict[str, Any]], dict[str, Any]], stamp: str,
          new_id: Callable[[], str]) -> list[dict[str, Any]]:
    """Sealed receipts for every registered kind the source returned, skipping an exact repeat of the latest one."""
    receipts: list[dict[str, Any]] = []
    for item in _collected(source, baseline, candidate):
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
                context: Context, policy_errors: list[str]) -> dict[str, Any]:
    """The formal part of the review packet: per-kind claims, blockers, the full evidence list, explanations."""
    verdicts = {k: aggregate_formal(k, receipts, subject, authenticator, context) for k in KINDS}
    return {"claims": {f"formal_{k}": v.status for k, v in verdicts.items()},
            "blockers": [f"FORMAL_EVIDENCE_{v.status}:{k}" for k, v in verdicts.items() if v.status in BLOCKING],
            "evidence": [_entry(KINDS[k], v, authenticator) for k, v in verdicts.items()],
            "explanations": _explanations(receipts, authenticator, verdicts, tuple(policy_errors)) if policy_errors else []}


# What an interpretation the policy refuses would MEAN in the model: the fault it would introduce. A what-if model is
# evaluated by the kernel's own policy and explained by the formal negative controls; it is never a candidate.
WHAT_IF_FAULTS = {"final_approval": ("Approve", "Teacher")}


def what_if_model(baseline: Workflow, interpretation: str) -> Workflow | None:
    """The workflow an unsupported interpretation would produce (recommendation enabled, the fault applied), or None."""
    fault = WHAT_IF_FAULTS.get(interpretation)
    if fault is None:
        return None
    data = apply_transaction(baseline, SemanticTransaction(kind="enable_recommendation")).model_dump(mode="json")
    for transition in data["transitions"]:
        if transition["action"] == fault[0]:
            transition["role"] = fault[1]
    return Workflow.model_validate(data)
