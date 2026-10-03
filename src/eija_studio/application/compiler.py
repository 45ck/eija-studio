"""Compiler: model → projections + impacts + obligations + computed review packet.

This is a bounded semantic/report compiler, not a general source-code compiler.
"""
from __future__ import annotations
from typing import Any, Callable
from eija_studio.domain.models import Workflow, fingerprint
from eija_studio.domain.change_case import ChangeCase
from eija_studio.domain.policy import projections, check_policy, meaning_questions
from eija_studio.domain.impact import model_impact
from eija_studio.domain.evidence import aggregate_status, expected_shape, receipt_status
from eija_studio.domain.pack import Pack, default_pack
from eija_studio.domain.formal import Context
from .formal import packet_view
from .witness_inspection import InspectionContext


def subject_for(model: Workflow, layout: dict[str, Any], identity: dict[str, Any]) -> dict[str, Any]:
    return {k: identity[k] for k in ("implementation", "policy", "environment", "harness")} | {
        "semantic": model.semantic_hash, "presentation": fingerprint(layout)}


def _resolve(pack: Pack | None) -> Pack:
    return pack if pack is not None else default_pack()


def compile_case(
    case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],
    active_version: int, scope: str = "local-demo", pack: Pack | None = None,
) -> dict[str, Any]:
    pack = _resolve(pack)
    if case.candidate is None:
        return {"eligible": False, "status": "BLOCKED", "blockers": ["MEANING_REQUIRED"], "human_understanding": "UNKNOWN"}
    model = case.candidate
    subject = subject_for(model, case.layout, identity)
    impact = model_impact(case.baseline, model)
    policy_errors = check_policy(model, pack)
    context = Context(candidate_semantic=model.semantic_hash, baseline_semantic=case.baseline.semantic_hash,
                      runtime=expected_shape(pack, model))
    evidence = aggregate_status(list(case.receipts), subject, authenticator, context)
    formal = packet_view(list(case.receipts), subject, authenticator, context, policy_errors, pack,
                         review_context=InspectionContext(case_id=case.id, case_version=case.version, scope=scope))
    blockers = []
    if policy_errors:
        blockers.append("POLICY_BLOCKED")
    if not identity["trusted_fixture"]:
        blockers.append("SOURCE_REVIEW_REQUIRED")
    if not impact["complete"]:
        blockers.append("IMPACT_INCOMPLETE")
    if evidence != "PASS":
        blockers.append("RUNTIME_EVIDENCE_" + evidence)
    blockers.extend(formal["blockers"])  # a formal counterexample (FAIL/CONFLICT) blocks; UNKNOWN and NOT_RUN never do
    if case.baseline_version != active_version and case.stage != "APPLIED":
        blockers.append("STALE_BASELINE")
    if scope != "local-demo":
        blockers.append("HUMAN_FIELD_EVIDENCE_REQUIRED")
    if case.stage == "DISCARDED":
        blockers.append("CASE_DISCARDED")
    return {"schema_version": "eija.review.v1", "scope": scope, "subject": subject,
        "subject_hash": fingerprint(subject), "eligible": not blockers,
        "status": "ELIGIBLE_FOR_LOCAL_REVIEW" if not blockers else "BLOCKED", "blockers": blockers,
        "policy_errors": policy_errors, "impact": impact, "projections": projections(model),
        "technical_claims": {"schema_policy": "FAIL" if policy_errors else "PASS", "runtime_matrix": evidence,
            "modelled_impact_closure": "PASS" if impact["complete"] else "UNKNOWN"} | formal["claims"],
        "formal_evidence": formal["evidence"], "explanations": formal["explanations"],
        "human_understanding": "UNKNOWN", "core_status": "RELEASE_FIXTURE_MATCH" if identity["trusted_fixture"] else "SOURCE_REVIEW_REQUIRED",
        "receipt_applicability": [{"id": r.get("id"), "kind": r.get("kind"), "status": receipt_status(r, subject, authenticator, context)}
             for r in case.receipts],
        "questions": meaning_questions(model, pack),
        "limitations": ["Human comprehension is not established by these checks or questions.",
            "Hash match identifies the shipped fixture; it is not an independent core review.",
            "Local owner is a single-user capability, not institutional identity or separation of duties.",
            "Impacts cover this model's explicit mapping, not all real-world dependencies.",
            "Formal evidence is about the models, bounds and assumptions listed per kind; UNKNOWN and NOT_RUN are never rounded up, and a proof about a model is not a proof about the code."]}
