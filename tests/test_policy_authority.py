"""Exact-oracle tests for the protected excursion policy (added by the mutation lane, ADR-0033).

The pre-existing policy tests assert that a bad model is *blocked* (`check_policy(model)` is non-empty).
Mutation analysis showed that is not enough: any error code, any wrong branch of the shape check, and
every string in the protected tables could change without a test noticing. These tests pin which rule
fired, for single-fault models, and pin the protected tables against independent literals. Expected
values come from the documented policy (docs/SECURITY_AND_TRUST.md, ADR-0000), not from the code.
"""
from __future__ import annotations

from typing import get_args

import pytest

from eija_studio.domain.models import DomainError, Interpretation, SemanticTransaction, Workflow
from eija_studio.domain.policy import (
    CANONICAL_OPTIONS, EFFECTS, FORBIDDEN, apply_transaction, baseline, check_policy, ensure_policy,
    meaning_questions, projections, transition)


def candidate() -> Workflow:
    return apply_transaction(baseline(), SemanticTransaction(kind="enable_recommendation"))


def edited(model: Workflow, action: str | None = None, /, **fields) -> Workflow:
    """A schema-valid copy with one transition (or top-level) field changed: a single-fault model."""
    data = model.model_dump(mode="json")
    if action is None:
        data.update(fields)
    else:
        next(t for t in data["transitions"] if t["action"] == action).update(fields)
    return Workflow.model_validate(data)


# ---- protected tables -------------------------------------------------------------------------------

def test_protected_tables_are_pinned_to_independent_literals():
    assert FORBIDDEN == ("PaymentCaptured", "ParentDataExported")
    assert EFFECTS == {
        "Submit": ("Audit:ExcursionSubmitted",),
        "Recommend": ("Audit:ExcursionRecommended", "Notification:RegistrarQueued"),
        "Approve": ("Audit:ExcursionApproved",),
        "Reject": ("Audit:ExcursionRejected",),
        "Revise": ("Audit:ExcursionReopened",),
    }


def test_only_recommend_only_is_a_supported_meaning():
    assert set(CANONICAL_OPTIONS) == set(get_args(Interpretation))
    assert {k for k, v in CANONICAL_OPTIONS.items() if v["supported"] is True} == {"recommend_only"}
    assert {k for k, v in CANONICAL_OPTIONS.items() if v["supported"] is False} == {"final_approval", "confirm_only", "unsupported"}
    for option in CANONICAL_OPTIONS.values():
        assert set(option) == {"label", "supported", "consequences"}
        assert option["label"] and option["consequences"]  # the service surfaces consequences[0] on refusal


def test_baseline_workflow_is_exactly_the_documented_excursion():
    model = baseline()
    assert model.states == ("Draft", "Submitted", "Approved", "Rejected")
    assert [(t.id, t.action, t.from_state, t.to_state, t.role) for t in model.transitions] == [
        ("TR-SUBMIT", "Submit", "Draft", "Submitted", "Teacher"),
        ("TR-APPROVE", "Approve", "Submitted", "Approved", "Registrar"),
        ("TR-REJECT", "Reject", "Submitted", "Rejected", "Registrar"),
        ("TR-REVISE", "Revise", "Rejected", "Draft", "Teacher"),
    ]
    assert all(t.forbidden_effects == FORBIDDEN for t in model.transitions)
    assert check_policy(model) == []


def test_transition_builder_adds_the_assignment_guard_only_for_recommend():
    assert "actor_assigned" in transition("Recommend", "Submitted", "Recommended", "Teacher").guards
    for action, source, target, role in [("Submit", "Draft", "Submitted", "Teacher"), ("Approve", "Submitted", "Approved", "Registrar")]:
        assert "actor_assigned" not in transition(action, source, target, role).guards


# ---- check_policy: which rule fired ----------------------------------------------------------------

def test_recommendation_candidate_conforms_and_baseline_conforms():
    assert check_policy(baseline()) == []
    assert check_policy(candidate()) == []


@pytest.mark.parametrize("build,expected", [
    (lambda: edited(baseline(), "Approve", role="Teacher"), ["PROTECTED_AUTHORITY:Approve"]),
    (lambda: edited(baseline(), "Submit", role="Registrar"), ["PROTECTED_AUTHORITY:Submit"]),
    (lambda: edited(candidate(), "Recommend", role="Registrar"), ["PROTECTED_AUTHORITY:Recommend"]),
    (lambda: edited(baseline(), "Approve", to_state="Rejected"), ["PROTECTED_STATE:Approve"]),
    (lambda: edited(baseline(), "Submit", from_state="Rejected"), ["PROTECTED_STATE:Submit"]),
    (lambda: edited(candidate(), "Approve", from_state="Submitted"), ["PROTECTED_STATE:Approve"]),
    (lambda: edited(candidate(), "Recommend", to_state="Approved"), ["PROTECTED_STATE:Recommend"]),
    (lambda: edited(baseline(), "Submit", guards=["actor_active", "role_current", "state_equals", "expected_version", "operation_binding", "actor_assigned"]), ["GUARD_POLICY:Submit"]),
    (lambda: edited(candidate(), "Recommend", guards=["actor_active", "role_current", "state_equals", "expected_version", "operation_binding"]), ["GUARD_POLICY:Recommend"]),
    (lambda: edited(baseline(), "Submit", required_effects=["Audit:ExcursionApproved"]), ["EFFECT_POLICY:Submit"]),
    (lambda: edited(candidate(), "Recommend", required_effects=["Audit:ExcursionRecommended"]), ["EFFECT_POLICY:Recommend"]),
    (lambda: edited(baseline(), "Approve", forbidden_effects=["PaymentCaptured"]), ["EFFECT_POLICY:Approve"]),
    (lambda: edited(baseline(), "Approve", forbidden_effects=["ParentDataExported"]), ["EFFECT_POLICY:Approve"]),
    (lambda: edited(baseline(), "Approve", forbidden_effects=[]), ["EFFECT_POLICY:Approve"]),
], ids=["approve-role", "submit-role", "recommend-role", "approve-target", "submit-source", "candidate-approve-source",
        "recommend-target", "submit-extra-guard", "recommend-no-assignment", "submit-effects", "recommend-effects",
        "no-export-ban", "no-payment-ban", "no-bans"])
def test_single_fault_models_are_blocked_by_exactly_the_rule_that_owns_them(build, expected):
    assert check_policy(build()) == expected


def test_extra_forbidden_effects_are_allowed_because_policy_requires_a_superset():
    assert check_policy(edited(baseline(), "Approve", forbidden_effects=[*FORBIDDEN, "SmsSent"])) == []


@pytest.mark.parametrize("build", [
    lambda: edited(baseline(), states=["Draft", "Submitted", "Approved", "Rejected", "Archived"]),
    lambda: edited(baseline(), states=["Draft", "Submitted", "Approved", "Rejected", "Recommended"]),
    lambda: edited(baseline(), initial_state="Submitted"),
    lambda: edited(candidate(), initial_state="Recommended"),
], ids=["extra-state", "recommended-state-without-recommend", "wrong-initial", "wrong-initial-candidate"])
def test_shape_check_fires_when_any_single_part_of_the_shape_is_wrong(build):
    """Each fault changes exactly one of: action set, state set, initial state (an `or`, not an `and`)."""
    assert check_policy(build()) == ["UNSUPPORTED_WORKFLOW_SHAPE"]


def test_missing_action_and_missing_state_are_shape_errors():
    data = baseline().model_dump(mode="json")
    data["transitions"] = [t for t in data["transitions"] if t["action"] != "Revise"]
    assert check_policy(Workflow.model_validate(data)) == ["UNSUPPORTED_WORKFLOW_SHAPE"]
    data = candidate().model_dump(mode="json")
    data["states"].remove("Recommended")
    data["transitions"] = [t for t in data["transitions"] if t["from_state"] != "Recommended" and t["to_state"] != "Recommended"]
    assert "UNSUPPORTED_WORKFLOW_SHAPE" in check_policy(Workflow.model_validate(data))


def test_unknown_action_is_reported_and_does_not_stop_later_checks():
    """`continue` after UNSUPPORTED_ACTION must move to the next transition, not abandon the rest."""
    data = baseline().model_dump(mode="json")
    escalate = {"id": "TR-ESCALATE", "action": "Escalate", "from_state": "Draft", "to_state": "Submitted", "role": "Teacher",
                "guards": data["transitions"][0]["guards"], "required_effects": ["Audit:Escalated"], "forbidden_effects": list(FORBIDDEN)}
    data["transitions"].insert(0, escalate)
    next(t for t in data["transitions"] if t["action"] == "Approve")["role"] = "Teacher"
    assert check_policy(Workflow.model_validate(data)) == ["PROTECTED_AUTHORITY:Approve", "UNSUPPORTED_ACTION", "UNSUPPORTED_WORKFLOW_SHAPE"]


def test_rejection_source_is_limited_to_submitted_or_recommended():
    assert check_policy(edited(candidate(), "Reject", from_state="Submitted")) == []
    assert check_policy(edited(candidate(), "Reject", from_state="Recommended")) == []
    for source in ("Draft", "Approved", "Rejected"):
        assert check_policy(edited(candidate(), "Reject", from_state=source)) == ["UNSUPPORTED_REJECTION_SOURCE"], source
    # Without the recommendation meaning, rejection must come from Submitted, and both rules say so.
    assert check_policy(edited(baseline(), "Reject", from_state="Draft")) == ["PROTECTED_STATE:Reject", "UNSUPPORTED_REJECTION_SOURCE"]


def test_rejection_target_is_protected_in_both_modes():
    assert check_policy(edited(candidate(), "Reject", to_state="Approved")) == ["PROTECTED_STATE:Reject"]
    assert check_policy(edited(baseline(), "Reject", to_state="Approved")) == ["PROTECTED_STATE:Reject"]


def test_errors_are_sorted_and_unique():
    model = edited(edited(baseline(), "Approve", role="Teacher"), "Submit", role="Registrar")
    errors = check_policy(model)
    assert errors == ["PROTECTED_AUTHORITY:Approve", "PROTECTED_AUTHORITY:Submit"] == sorted(set(errors))


# ---- ensure_policy / apply_transaction -------------------------------------------------------------

def test_ensure_policy_blocks_with_a_stable_code_and_lists_every_error():
    assert ensure_policy(baseline()) is None
    model = edited(edited(baseline(), "Approve", role="Teacher"), "Submit", role="Registrar")
    with pytest.raises(DomainError) as info:
        ensure_policy(model)
    assert info.value.code == "POLICY_BLOCKED"
    assert info.value.message == "PROTECTED_AUTHORITY:Approve; PROTECTED_AUTHORITY:Submit"


def test_apply_transaction_refuses_to_start_from_a_policy_violating_model():
    with pytest.raises(DomainError) as info:
        apply_transaction(edited(baseline(), "Approve", role="Teacher"), SemanticTransaction(kind="enable_recommendation"))
    assert info.value.code == "POLICY_BLOCKED"


def test_enabling_recommendation_moves_authority_exactly_as_documented():
    model = candidate()
    assert model.states == ("Draft", "Submitted", "Recommended", "Approved", "Rejected")
    by = {t.action: t for t in model.transitions}
    assert (by["Recommend"].role, by["Recommend"].from_state, by["Recommend"].to_state) == ("Teacher", "Submitted", "Recommended")
    assert "actor_assigned" in by["Recommend"].guards
    assert by["Recommend"].required_effects == ("Audit:ExcursionRecommended", "Notification:RegistrarQueued")
    assert (by["Approve"].role, by["Approve"].from_state) == ("Registrar", "Recommended")
    assert (by["Reject"].role, by["Reject"].from_state) == ("Registrar", "Recommended")  # default rejection source
    assert {t.role for t in model.transitions if t.action in {"Approve", "Reject"}} == {"Registrar"}


def test_enabling_recommendation_twice_is_idempotent_not_a_duplicate_transition():
    assert apply_transaction(candidate(), SemanticTransaction(kind="enable_recommendation")) == candidate()


def test_rejection_source_can_only_be_set_after_the_meaning_is_enabled():
    with pytest.raises(DomainError) as info:
        apply_transaction(baseline(), SemanticTransaction(kind="set_rejection_source"))
    assert info.value.code == "MEANING_REQUIRED"
    widened = apply_transaction(candidate(), SemanticTransaction(kind="set_rejection_source", rejection_source="Submitted"))
    assert next(t for t in widened.transitions if t.action == "Reject").from_state == "Submitted"
    narrowed = apply_transaction(widened, SemanticTransaction(kind="set_rejection_source", rejection_source="Recommended"))
    assert narrowed == candidate()


# ---- derived views ---------------------------------------------------------------------------------

def test_projections_are_derived_from_the_executable_transitions():
    model = baseline()
    view = projections(model)
    assert set(view) == {"rules", "states", "journeys"}
    assert view["rules"] == [t.model_dump(mode="json") for t in model.transitions]
    assert view["journeys"] == [
        "Teacher: Draft → Submit → Submitted",
        "Registrar: Submitted → Approve → Approved",
        "Registrar: Submitted → Reject → Rejected",
        "Teacher: Rejected → Revise → Draft",
    ]
    assert view["states"] == [
        {"id": "Draft", "next_actions": [{"action": "Submit", "role": "Teacher", "target": "Submitted"}]},
        {"id": "Submitted", "next_actions": [{"action": "Approve", "role": "Registrar", "target": "Approved"},
                                             {"action": "Reject", "role": "Registrar", "target": "Rejected"}]},
        {"id": "Approved", "next_actions": []},
        {"id": "Rejected", "next_actions": [{"action": "Revise", "role": "Teacher", "target": "Draft"}]},
    ]


def test_review_questions_name_the_rejection_entry_state_of_the_current_model():
    def answers(model):
        return [(q["id"], q["expected"]) for q in meaning_questions(model)]
    assert answers(baseline()) == [("authority", "Registrar"), ("assignment", "No"), ("reject_entry", "Submitted")]
    assert answers(candidate()) == [("authority", "Registrar"), ("assignment", "No"), ("reject_entry", "Recommended")]
    assert all(set(q) == {"id", "question", "expected"} and q["question"].endswith("?") for q in meaning_questions(baseline()))
