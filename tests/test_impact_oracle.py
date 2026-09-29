"""Exact-oracle tests of impact analysis (`domain/impact.py`), added by the mutation lane (ADR-0033).

`closure` is a fixed-point traversal with an explicit budget: it must never silently truncate, and a
budgeted result must name the frontier it did not reach. `model_impact` maps changed transitions onto the
documented dependency chain rule -> runtime -> state view -> journey -> obligation -> receipt -> review
packet -> local decision. Expected values are written out by hand from those definitions.
"""
from __future__ import annotations

import pytest

from eija_studio.domain.impact import closure, model_impact
from eija_studio.domain.models import SemanticTransaction, Workflow
from eija_studio.domain.policy import apply_transaction, baseline

CHAIN = ("rule", "runtime", "state-view", "journey", "obligation", "receipt")
TAIL = ("review-packet", "local-decision")


def candidate() -> Workflow:
    return apply_transaction(baseline(), SemanticTransaction(kind="enable_recommendation"))


def chain_nodes(action: str) -> list[str]:
    return [f"{kind}:{action}" for kind in CHAIN] + list(TAIL)


# ---- closure ---------------------------------------------------------------------------------------

def test_closure_reaches_every_dependent_once_and_sorts_the_result():
    graph = {"a": ["c", "b"], "b": ["d"], "c": ["d"], "z": ["a"]}
    assert closure(graph, ["a"]) == {"affected": ["a", "b", "c", "d"], "complete": True, "frontier": []}


def test_edges_mean_source_affects_target_not_the_reverse():
    assert closure({"a": ["b"]}, ["b"]) == {"affected": ["b"], "complete": True, "frontier": []}


def test_roots_are_deduplicated_and_need_not_appear_in_the_graph():
    assert closure({}, ["b", "a", "b"]) == {"affected": ["a", "b"], "complete": True, "frontier": []}
    assert closure({"a": ["b"]}, []) == {"affected": [], "complete": True, "frontier": []}


def test_cycles_terminate_and_include_every_member_once():
    assert closure({"a": ["b"], "b": ["c"], "c": ["a"]}, ["b"]) == {"affected": ["a", "b", "c"], "complete": True, "frontier": []}


def test_a_budget_stops_after_that_many_nodes_and_names_the_frontier():
    graph = {"a": ["b"], "b": ["c", "d"], "c": ["e"]}
    assert closure(graph, ["a"], budget=1) == {"affected": ["a"], "complete": False, "frontier": ["b"]}
    assert closure(graph, ["a"], budget=2) == {"affected": ["a", "b"], "complete": False, "frontier": ["c", "d"]}
    assert closure(graph, ["a"], budget=0) == {"affected": [], "complete": False, "frontier": ["a"]}


def test_a_budget_exactly_large_enough_is_complete():
    graph = {"a": ["b"], "b": ["c"]}
    assert closure(graph, ["a"], budget=3) == {"affected": ["a", "b", "c"], "complete": True, "frontier": []}
    assert closure(graph, ["a"], budget=4) == {"affected": ["a", "b", "c"], "complete": True, "frontier": []}
    assert closure({}, [], budget=0) == {"affected": [], "complete": True, "frontier": []}


def test_a_visited_node_is_never_reported_as_frontier():
    graph = {"a": ["b", "c"], "b": ["c"]}
    assert closure(graph, ["a"], budget=2) == {"affected": ["a", "b"], "complete": False, "frontier": ["c"]}


def test_a_negative_budget_is_an_error_not_unlimited():
    with pytest.raises(ValueError, match="Negative traversal budget"):
        closure({"a": []}, ["a"], budget=-1)


# ---- model_impact ----------------------------------------------------------------------------------

def test_no_change_has_no_impact():
    report = model_impact(baseline(), baseline())
    assert report["changed_actions"] == [] and report["affected"] == [] and report["complete"] is True and report["frontier"] == []


def test_enabling_recommendation_changes_three_actions_and_reaches_the_decision():
    report = model_impact(baseline(), candidate())
    assert report["changed_actions"] == ["Approve", "Recommend", "Reject"]
    expected = sorted({node for action in report["changed_actions"] for node in chain_nodes(action)})
    assert report["affected"] == expected
    assert report["complete"] is True and report["frontier"] == []
    assert "local-decision" in report["affected"] and "review-packet" in report["affected"]
    assert not any(node.endswith(":Submit") or node.endswith(":Revise") for node in report["affected"])


def test_the_dependency_graph_is_the_documented_chain_for_every_action_in_either_model():
    report = model_impact(baseline(), candidate())
    graph = report["graph"]
    for action in ("Submit", "Recommend", "Approve", "Reject", "Revise"):
        nodes = chain_nodes(action)
        for source, target in zip(nodes, nodes[1:]):
            assert target in graph[source], (source, target)
    assert graph["receipt:Approve"] == ["review-packet"]
    assert graph["review-packet"] == ["local-decision"] * 5  # one edge per action, appended (not deduplicated)
    assert "local-decision" not in graph
    assert set(graph) == {node for action in ("Submit", "Recommend", "Approve", "Reject", "Revise") for node in chain_nodes(action)[:-1]}


def test_a_change_to_a_single_action_affects_only_that_actions_chain():
    changed = candidate().model_dump(mode="json")
    next(t for t in changed["transitions"] if t["action"] == "Submit")["required_effects"] = ["Audit:ExcursionSubmitted", "Audit:Extra"]
    report = model_impact(candidate(), Workflow.model_validate(changed))
    assert report["changed_actions"] == ["Submit"]
    assert report["affected"] == sorted(chain_nodes("Submit"))


def test_impact_is_symmetric_in_the_changed_set_and_states_its_envelope():
    forward, backward = model_impact(baseline(), candidate()), model_impact(candidate(), baseline())
    assert forward["changed_actions"] == backward["changed_actions"] and forward["affected"] == backward["affected"]
    assert forward["envelope"].startswith("All dependencies encoded by this excursion projection mapping")
    assert "not every real-world consequence" in forward["envelope"]
