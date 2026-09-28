import copy
import pytest
from pydantic import ValidationError
from eija_studio.domain.models import Workflow, SemanticTransaction, Proposal
from eija_studio.domain.policy import baseline, apply_transaction, check_policy, projections
from eija_studio.domain.impact import closure, model_impact


def candidate():
    return apply_transaction(baseline(), SemanticTransaction(kind="enable_recommendation"))


def test_unknown_fields_and_operators_are_rejected():
    data = candidate().model_dump(mode="json")
    data["approved"] = True
    with pytest.raises(ValidationError): Workflow.model_validate(data)
    data.pop("approved"); data["transitions"][0]["guards"].append("eval_python")
    with pytest.raises(ValidationError): Workflow.model_validate(data)


def test_mandatory_guard_cannot_be_removed():
    data = candidate().model_dump(mode="json"); data["transitions"][0]["guards"].remove("role_current")
    with pytest.raises(ValidationError): Workflow.model_validate(data)


def test_duplicate_and_dangling_transitions_rejected():
    data = candidate().model_dump(mode="json"); data["transitions"].append(data["transitions"][0])
    with pytest.raises(ValidationError): Workflow.model_validate(data)
    data = candidate().model_dump(mode="json"); data["transitions"][0]["to_state"] = "Absent"
    with pytest.raises(ValidationError): Workflow.model_validate(data)


def test_semantic_hash_definition_order_is_irrelevant():
    model=candidate(); data=model.model_dump(mode="json")
    data["states"].reverse(); data["transitions"].reverse()
    for t in data["transitions"]: t["guards"].reverse()
    assert model.semantic_hash == Workflow.model_validate(data).semantic_hash


def test_semantic_hash_rule_change_is_relevant():
    model = candidate()
    changed = apply_transaction(model, SemanticTransaction(kind="set_rejection_source", rejection_source="Submitted"))
    assert model.semantic_hash != changed.semantic_hash


def test_projections_do_not_leave_registrar_as_next_actor_in_submitted():
    view = projections(candidate())
    submitted = next(s for s in view["states"] if s["id"] == "Submitted")
    assert submitted["next_actions"] == [{"action": "Recommend", "role": "Teacher", "target": "Recommended"}]


def test_deep_chain_and_cycle_closure():
    graph = {str(i): [str(i+1)] for i in range(1000)}; graph["1000"]=["0"]
    result=closure(graph,["0"])
    assert result["complete"] and len(result["affected"]) == 1001
    assert set(result["affected"]) == {str(i) for i in range(1001)}


def test_impact_budget_reports_explicit_frontier():
    result=closure({"a":["b"],"b":["c"],"c":["d"]},["a"],budget=2)
    assert result == {"affected":["a","b"],"complete":False,"frontier":["c"]}
    assert closure({"a":["a"]},["a"],budget=1)["complete"]


def test_full_modelled_impact_goes_beyond_five_edges():
    result=model_impact(baseline(),candidate())
    assert result["complete"] and "local-decision" in result["affected"]
    assert result["changed_actions"] == ["Approve","Recommend","Reject"]

@pytest.mark.parametrize("action,field,value",[
    ("Approve","role","Teacher"), ("Recommend","role","Registrar"),
    ("Recommend","to_state","Approved"), ("Approve","from_state","Submitted"),
    ("Reject","to_state","Approved"), ("Recommend","guards",["actor_active","role_current","state_equals","expected_version","operation_binding"]),
    ("Recommend","required_effects",["PaymentCaptured"]), ("Recommend","required_effects",["ParentDataExported"]),
    ("Recommend","required_effects",["Audit:ExcursionRecommended"]),
])
def test_protected_policy_mutants_blocked(action,field,value):
    data=candidate().model_dump(mode="json"); t=next(t for t in data["transitions"] if t["action"]==action)
    t[field]=value
    try: model=Workflow.model_validate(data)
    except ValidationError: return
    assert check_policy(model), "Unsafe mutation escaped both schema and protected policy"


def test_proposal_cannot_contain_proof_or_approval_fields():
    data={"summary":"test","alternatives":[{"interpretation":"recommend_only","explanation":"x"}],"unknowns":[],"approved":True}
    with pytest.raises(ValidationError): Proposal.model_validate(data)
