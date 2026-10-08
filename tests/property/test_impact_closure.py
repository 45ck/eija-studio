"""Impact closure (``domain.impact.closure``): a fixed point over a dependency graph.

The oracle is a plain depth-first reachability written here. Properties: the unbudgeted closure equals
reachability, contains its roots, is idempotent, monotone in the roots and distributes over union;
cycles terminate; a traversal budget never returns more than the budget, never invents nodes, reports
exactly the un-visited boundary as ``frontier``, and reports ``complete`` if and only if nothing
reachable was left out.

What this establishes: the traversal is a correct closure operator on arbitrary graphs (including
self-loops, cycles and roots absent from the graph). What it does NOT establish: that the projection
graph built by ``model_impact`` covers every real-world consequence (its own ``envelope`` says so).
"""
from __future__ import annotations

import copy

import pytest
from hypothesis import given, settings, strategies as st

from eija_studio.domain.impact import closure, model_impact
from .property_strategies import semantic_edits, workflows
from .property_support import examples

NODES = st.sampled_from(list("abcdefghij"))
GRAPHS = st.dictionaries(NODES, st.lists(NODES, max_size=5), max_size=10)
ROOTS = st.lists(NODES, max_size=6)


def reachable(graph: dict[str, list[str]], roots: list[str]) -> set[str]:
    """Reference reachability: iterative depth-first search, roots included."""
    seen: set[str] = set()
    stack = list(roots)
    while stack:
        node = stack.pop()
        if node not in seen:
            seen.add(node)
            stack.extend(graph.get(node, []))
    return seen


@settings(max_examples=examples(300))
@given(GRAPHS, ROOTS)
def test_closure_is_reachability(graph, roots):
    report = closure(graph, roots)
    assert set(report["affected"]) == reachable(graph, roots)
    assert report["affected"] == sorted(set(report["affected"]))
    assert report["complete"] is True and report["frontier"] == []
    assert set(roots) <= set(report["affected"])


@settings(max_examples=examples(200))
@given(GRAPHS, ROOTS)
def test_closure_is_idempotent(graph, roots):
    affected = closure(graph, roots)["affected"]
    assert closure(graph, affected)["affected"] == affected


@settings(max_examples=examples(200))
@given(GRAPHS, ROOTS, ROOTS)
def test_closure_is_monotone_and_distributes_over_union(graph, first, second):
    small, large = set(closure(graph, first)["affected"]), set(closure(graph, first + second)["affected"])
    assert small <= large
    assert large == small | set(closure(graph, second)["affected"])


@settings(max_examples=examples(100))
@given(GRAPHS, ROOTS)
def test_closure_does_not_mutate_its_inputs(graph, roots):
    before = copy.deepcopy((graph, roots))
    closure(graph, roots)
    closure(graph, roots, budget=1)
    assert (graph, roots) == before


@settings(max_examples=examples(60))
@given(st.integers(1, 40), st.booleans())
def test_long_cycles_terminate(length, self_loop):
    """A ring (and a ring with a self-loop) is finite; the fixed point visits each node once."""
    graph = {str(i): [str((i + 1) % length)] for i in range(length)}
    if self_loop:
        graph["0"].append("0")
    report = closure(graph, ["0"])
    assert report["affected"] == sorted(str(i) for i in range(length)) and report["complete"] is True


@settings(max_examples=examples(400))
@given(GRAPHS, ROOTS, st.integers(0, 12))
def test_budget_reports_a_correct_frontier(graph, roots, budget):
    full = reachable(graph, roots)
    report = closure(graph, roots, budget=budget)
    affected, frontier = set(report["affected"]), set(report["frontier"])
    assert len(affected) <= budget                      # the budget is honoured
    assert affected <= full and frontier <= full        # nothing is invented
    assert not affected & frontier                      # the frontier is unvisited
    assert report["frontier"] == sorted(frontier)
    assert report["complete"] == (affected == full)     # complete iff nothing reachable was left out
    assert report["complete"] == (not frontier)
    # Every frontier node is a root or an immediate successor of an affected node ...
    assert all(node in roots or any(node in graph.get(a, []) for a in affected) for node in frontier)
    # ... and nothing reachable is lost: the affected set plus the frontier still reaches everything.
    assert reachable(graph, sorted(affected | frontier)) == full
    if budget >= len(full):
        assert report == closure(graph, roots)


@settings(max_examples=examples(200))
@given(GRAPHS, ROOTS, st.integers(0, 10))
def test_budgeted_closure_grows_with_the_budget(graph, roots, budget):
    smaller, larger = closure(graph, roots, budget=budget), closure(graph, roots, budget=budget + 1)
    assert set(smaller["affected"]) <= set(larger["affected"])


def test_negative_budget_is_rejected():
    with pytest.raises(ValueError):
        closure({}, ["a"], budget=-1)


@settings(max_examples=examples(150))
@given(st.data())
def test_model_impact_covers_exactly_the_changed_actions(data):
    """Changed actions are the symmetric difference of the two action->transition maps, computed here
    independently; every changed action reaches the review packet and the local decision."""
    before = data.draw(workflows())
    _, after = data.draw(semantic_edits(before))
    report = model_impact(before, after)
    old, new = {t.action: t for t in before.transitions}, {t.action: t for t in after.transitions}
    expected = sorted(a for a in old.keys() | new.keys() if old.get(a) != new.get(a))
    assert report["changed_actions"] == expected
    assert report["complete"] is True and report["frontier"] == []
    if expected:
        assert {"review-packet", "local-decision"} <= set(report["affected"])
        assert all(f"rule:{a}" in report["affected"] and f"receipt:{a}" in report["affected"] for a in expected)
    else:
        assert report["affected"] == []
    unchanged = {a for a in old.keys() & new.keys() if old[a] == new[a]}
    assert not any(f"rule:{a}" in report["affected"] for a in unchanged)
