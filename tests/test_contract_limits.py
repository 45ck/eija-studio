"""Boundary and identity tests of the typed contracts (`domain/models.py`), added by the mutation lane (ADR-0033).

Every `Field(min_length=..., max_length=..., ge=..., le=...)` is a trust boundary: a provider or HTTP client
controls the value. Mutation analysis showed the limits could move by one without any test noticing. Each
case here pins the last accepted and the first rejected value. The limits themselves are the documented
contract (docs/architecture/ARCHITECTURE.md, contracts/), restated here as literals on purpose.
"""
from __future__ import annotations

import hashlib

import pytest
from pydantic import ValidationError

from eija_studio.domain.models import (
    AGENT, OWNER, Alternative, DomainError, ExecuteCommand, LayoutChange, Principal, Proposal, SemanticTransaction,
    Transition, Workflow, canonical, fingerprint)
from eija_studio.domain.policy import baseline


def transition_data(**changes) -> dict:
    return baseline().transitions[0].model_dump(mode="json") | changes


def accepts(model, data) -> bool:
    try:
        model.model_validate(data)
    except ValidationError:
        return False
    return True


def assert_bounds(model, base: dict, name: str, ok: list, bad: list) -> None:
    for value in ok:
        assert accepts(model, base | {name: value}), f"{model.__name__}.{name} should accept {value!r:.40}"
    for value in bad:
        assert not accepts(model, base | {name: value}), f"{model.__name__}.{name} should reject {value!r:.40}"


# ---- text length limits ----------------------------------------------------------------------------

@pytest.mark.parametrize("name", ["action", "from_state", "to_state", "role"])
def test_transition_text_fields_are_1_to_60_characters(name):
    assert_bounds(Transition, transition_data(), name, ["x", "x" * 60], ["", "x" * 61])


def test_transition_id_is_an_upper_case_token_of_1_to_64_characters():
    assert_bounds(Transition, transition_data(), "id", ["A", "A" * 64, "TR-SUBMIT", "A_1-2"], ["", "A" * 65, "tr-submit", "1A", "-A", "A B", "A\n"])


@pytest.mark.parametrize("name,limit", [("action", 60), ("actor_id", 80), ("instance_id", 80)])
def test_command_text_fields_have_their_limits(name, limit):
    base = {"operation_id": "op", "actor_id": "a", "instance_id": "i", "action": "Submit", "expected_version": 0}
    assert_bounds(ExecuteCommand, base, name, ["x", "x" * limit], ["", "x" * (limit + 1)])


def test_command_operation_id_is_a_token_of_1_to_100_characters():
    base = {"operation_id": "op", "actor_id": "a", "instance_id": "i", "action": "Submit", "expected_version": 0}
    assert_bounds(ExecuteCommand, base, "operation_id", ["a", "A-z_9", "x" * 100], ["", "x" * 101, "a b", "a/b", "a.b", "é"])


def test_command_version_is_a_non_negative_strict_integer():
    base = {"operation_id": "op", "actor_id": "a", "instance_id": "i", "action": "Submit", "expected_version": 0}
    assert_bounds(ExecuteCommand, base, "expected_version", [0, 1, 10**6], [-1, "1", 1.0, True, None])


def test_layout_change_limits():
    base = {"node": "Draft", "x": 0, "y": 0}
    assert_bounds(LayoutChange, base, "node", ["n", "n" * 60], ["", "n" * 61])
    for axis in ("x", "y"):
        assert_bounds(LayoutChange, base, axis, [0, 1, 1999, 2000], [-1, 2001])


def test_alternative_explanation_and_proposal_summary_are_1_to_1600_characters():
    assert_bounds(Alternative, {"interpretation": "recommend_only", "explanation": "x"}, "explanation", ["x", "x" * 1600], ["", "x" * 1601])
    base = {"summary": "s", "alternatives": [{"interpretation": "recommend_only", "explanation": "x"}], "unknowns": []}
    assert_bounds(Proposal, base, "summary", ["s", "s" * 1600], ["", "s" * 1601])


def test_proposal_unknowns_are_at_most_ten_items_of_at_most_1600_characters():
    base = {"summary": "s", "alternatives": [{"interpretation": "recommend_only", "explanation": "x"}], "unknowns": []}
    assert_bounds(Proposal, base, "unknowns", [[], ["u"], ["u"] * 10, ["u" * 1600]], [["u"] * 11, ["u" * 1601]])


def test_proposal_has_one_to_four_distinct_alternatives():
    def alt(name):
        return {"interpretation": name, "explanation": "x"}
    base = {"summary": "s", "alternatives": [alt("recommend_only")], "unknowns": []}
    names = ["recommend_only", "final_approval", "confirm_only", "unsupported"]
    assert_bounds(Proposal, base, "alternatives", [[alt(n) for n in names[:k]] for k in (1, 2, 3, 4)],
                  [[], [alt("recommend_only"), alt("recommend_only")], [alt("Not a meaning id")]])
    # Any well-formed meaning id is a valid proposal; whether the pack models it is checked at selection (INTERPRETATION_MISSING /
    # MEANING_UNSUPPORTED), not by the contract.


def test_proposal_and_transactions_reject_unknown_fields_and_values():
    base = {"summary": "s", "alternatives": [{"interpretation": "recommend_only", "explanation": "x"}], "unknowns": []}
    assert not accepts(Proposal, base | {"approved": True})
    assert accepts(SemanticTransaction, {"kind": "enable_recommendation"})
    assert not accepts(SemanticTransaction, {"kind": "grant_teacher_approval"})
    assert not accepts(SemanticTransaction, {"kind": "set_rejection_source", "rejection_source": "Draft"})
    assert SemanticTransaction(kind="set_rejection_source").rejection_source == "Recommended"


# ---- workflow size and coherence -------------------------------------------------------------------

def workflow_data(states: int = 4, transitions: int = 1) -> dict:
    names = ["Draft"] + [f"S{i}" for i in range(1, states)]
    rows = [transition_data(id=f"TR-{i}", action=f"Act{i}", from_state="Draft", to_state=names[i % len(names)], role="Teacher") for i in range(transitions)]
    return {"id": "excursion", "initial_state": "Draft", "states": names, "transitions": rows}


def test_workflow_state_count_is_1_to_32():
    assert accepts(Workflow, workflow_data(states=1)) and accepts(Workflow, workflow_data(states=32))
    assert not accepts(Workflow, workflow_data(states=33))
    assert not accepts(Workflow, workflow_data(states=1) | {"states": []})


def test_workflow_transition_count_is_1_to_64():
    assert accepts(Workflow, workflow_data(transitions=1)) and accepts(Workflow, workflow_data(transitions=64))
    assert not accepts(Workflow, workflow_data(transitions=65))
    assert not accepts(Workflow, workflow_data() | {"transitions": []})


@pytest.mark.parametrize("edit,why", [
    (lambda d: d["transitions"][1].update(id=d["transitions"][0]["id"]), "same id, different action"),
    (lambda d: d["transitions"][1].update(action=d["transitions"][0]["action"]), "same action, different id"),
    (lambda d: d["transitions"][1].update(action=d["transitions"][0]["action"], from_state="S1"), "same action from another state"),
    (lambda d: d["transitions"][1].update(from_state="Nowhere"), "dangling source"),
    (lambda d: d["transitions"][1].update(to_state="Nowhere"), "dangling target"),
    (lambda d: d.update(states=d["states"] + ["Draft"]), "duplicate state"),
    (lambda d: d.update(initial_state="Nowhere"), "initial state missing"),
])
def test_incoherent_workflows_are_rejected_each_for_its_own_reason(edit, why):
    data = workflow_data(states=3, transitions=2)
    assert accepts(Workflow, data)
    edit(data)
    assert not accepts(Workflow, data), why


def test_a_transition_may_reuse_a_source_target_and_role_when_actions_differ():
    data = workflow_data(states=3, transitions=3)
    assert accepts(Workflow, data)


@pytest.mark.parametrize("edit,why", [
    (lambda t: t.update(guards=[g for g in t["guards"] if g != "state_equals"]), "mandatory guard removed"),
    (lambda t: t.update(guards=t["guards"] + ["actor_active"]), "duplicate guard"),
    (lambda t: t.update(guards=t["guards"] + ["eval_python"]), "unknown guard"),
    (lambda t: t.update(required_effects=["Audit:A", "Audit:A"]), "duplicate required effect"),
    (lambda t: t.update(required_effects=["X"], forbidden_effects=["X"]), "required and forbidden overlap"),
])
def test_transition_invariants(edit, why):
    data = transition_data()
    edit(data)
    assert not accepts(Transition, data), why
    assert accepts(Transition, transition_data(guards=transition_data()["guards"] + ["actor_assigned"]))


# ---- identity and serialisation --------------------------------------------------------------------

def test_canonical_form_is_sorted_compact_utf8_and_rejects_nan():
    assert canonical({"b": [1, 2], "a": "é"}) == '{"a":"é","b":[1,2]}'
    assert canonical(Alternative(interpretation="unsupported", explanation="x")) == '{"explanation":"x","interpretation":"unsupported"}'
    with pytest.raises(ValueError):
        canonical({"x": float("nan")})


def test_canonical_form_of_a_model_uses_json_serialisable_values():
    principal = Principal(id="p", capabilities=frozenset({"select"}))
    assert canonical(principal) == '{"capabilities":["select"],"id":"p"}'


def test_fingerprint_is_the_sha256_of_the_canonical_form():
    assert fingerprint({"a": 1}) == hashlib.sha256(b'{"a":1}').hexdigest()
    assert fingerprint({"a": 1}) != fingerprint({"a": 2})


def test_semantic_hash_ignores_definition_order_but_not_meaning():
    model = baseline()
    data = model.model_dump(mode="json")
    data["states"].reverse()
    data["transitions"].reverse()
    for t in data["transitions"]:
        t["guards"].reverse()
        t["required_effects"].reverse()
    assert Workflow.model_validate(data).semantic_hash == model.semantic_hash
    for edit in (lambda d: d["states"].__setitem__(0, "Started") or d.update(initial_state="Started"),
                 lambda d: d["transitions"][0].update(role="Registrar"),
                 lambda d: d["transitions"][0].update(guards=d["transitions"][0]["guards"] + ["actor_assigned"]),
                 lambda d: d["transitions"][0].update(forbidden_effects=["PaymentCaptured"])):
        changed = model.model_dump(mode="json")
        edit(changed)
        try:
            other = Workflow.model_validate(changed)
        except ValidationError:
            continue
        assert other.semantic_hash != model.semantic_hash


def test_semantic_hash_covers_transition_effects_regardless_of_their_order():
    a, b = baseline().model_dump(mode="json"), baseline().model_dump(mode="json")
    b["transitions"][0]["required_effects"] = ["Audit:Other"]
    assert Workflow.model_validate(a).semantic_hash != Workflow.model_validate(b).semantic_hash


def test_contracts_are_immutable_and_forbid_extra_fields():
    model = baseline()
    with pytest.raises(ValidationError):
        model.initial_state = "Approved"
    assert not accepts(Workflow, model.model_dump(mode="json") | {"approved": True})


# ---- domain errors and principals ------------------------------------------------------------------

def test_domain_error_carries_a_stable_code_and_message():
    error = DomainError("SOME_CODE", "human text")
    assert (error.code, error.message, str(error)) == ("SOME_CODE", "human text", "human text")
    assert isinstance(error, ValueError)


def test_capabilities_are_required_exactly_and_agents_hold_none():
    for capability in ("select", "edit", "approve", "apply"):
        OWNER.require(capability)
    assert OWNER.capabilities == frozenset({"select", "edit", "approve", "apply"}) and OWNER.id == "local-owner"
    assert AGENT.capabilities == frozenset() and AGENT.id == "agent"
    for principal, capability in ((AGENT, "select"), (AGENT, "approve"), (OWNER, "sudo")):
        with pytest.raises(DomainError) as info:
            principal.require(capability)
        assert info.value.code == "AUTHORITY_REQUIRED" and info.value.message == f"Capability required: {capability}"
