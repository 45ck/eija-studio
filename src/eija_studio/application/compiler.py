"""Compiler: model → projections + impacts + obligations + computed review packet.

This is a bounded semantic/report compiler, not a general source-code compiler.
"""
from __future__ import annotations
from typing import Any, Callable
from eija_studio.domain.models import Workflow, fingerprint
from eija_studio.domain.change_case import ChangeCase
from eija_studio.domain.policy import projections, check_policy, meaning_questions
from eija_studio.domain.impact import model_impact
from eija_studio.domain.evidence import aggregate_status, assess_receipt


def subject_for(model: Workflow, layout: dict[str, Any], identity: dict[str, Any]) -> dict[str, Any]:
    return {k: identity[k] for k in ("implementation", "policy", "environment", "harness")} | {
        "semantic": model.semantic_hash, "presentation": fingerprint(layout)}


def compile_case(
    case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],
    active_version: int, scope: str = "local-demo",
) -> dict[str, Any]:
    if case.candidate is None:
        return {"eligible": False, "status": "BLOCKED", "blockers": ["MEANING_REQUIRED"], "human_understanding": "UNKNOWN"}
    model = case.candidate
    subject = subject_for(model, case.layout, identity)
    impact = model_impact(case.baseline, model)
    policy_errors = check_policy(model)
    evidence = aggregate_status(list(case.receipts), subject, authenticator)
    blockers = []
    if policy_errors:
        blockers.append("POLICY_BLOCKED")
    if not identity["trusted_fixture"]:
        blockers.append("SOURCE_REVIEW_REQUIRED")
    if not impact["complete"]:
        blockers.append("IMPACT_INCOMPLETE")
    if evidence != "PASS":
        blockers.append("RUNTIME_EVIDENCE_" + evidence)
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
            "modelled_impact_closure": "PASS" if impact["complete"] else "UNKNOWN"},
        "human_understanding": "UNKNOWN", "core_status": "RELEASE_FIXTURE_MATCH" if identity["trusted_fixture"] else "SOURCE_REVIEW_REQUIRED",
        "receipt_applicability": [{"id": r.get("id"), "status": assess_receipt(r, subject, "runtime_matrix", "integration_test")
             if authenticator(r) else "FAIL"} for r in case.receipts],
        "questions": meaning_questions(model),
        "limitations": ["Human comprehension is not established by these checks or questions.",
            "Hash match identifies the shipped fixture; it is not an independent core review.",
            "Local owner is a single-user capability, not institutional identity or separation of duties.",
            "Impacts cover this model's explicit mapping, not all real-world dependencies."]}
