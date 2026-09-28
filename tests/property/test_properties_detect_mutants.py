"""Negative controls for the non-stateful properties: each is run against a deliberately broken
implementation and must fail with an ``AssertionError``.

A property that cannot fail is not evidence. The broken implementations are installed by
``monkeypatch`` in the test module under examination (or on the class, for the hash) and vanish after
the test; nothing here changes the shipped kernel. The stateful differential mutants are in
``test_reference_detects_mutants.py``.
"""
from __future__ import annotations

import copy
from collections import deque
from contextlib import contextmanager

import pytest
from hypothesis import Phase, settings

from . import test_contract_schemas as contracts
from . import test_impact_closure as impact
from . import test_receipts as receipts
from . import test_semantic_hash as hashing
from eija_studio.domain.evidence import assess_receipt as real_assess
from eija_studio.domain.impact import closure as real_closure
from eija_studio.domain.models import Workflow, fingerprint

@contextmanager
def falsification_only(prop):
    """Run ``prop`` without the shrink phase: a mutant only has to be *found*, and shrinking a failure
    costs minutes. Uses the attribute Hypothesis' own pytest plugin sets for the same purpose; the
    version is pinned, and a missing attribute fails loudly rather than silently shrinking."""
    original = prop._hypothesis_internal_use_settings
    prop._hypothesis_internal_use_settings = settings(original, phases=[Phase.explicit, Phase.reuse, Phase.generate],
                                                      report_multiple_bugs=False)
    try:
        yield prop
    finally:
        prop._hypothesis_internal_use_settings = original


# --- hash mutants ------------------------------------------------------------------------------------


def hash_variant(*, sort_guards=True, sort_states=True, sort_transitions=True, drop=()):
    def semantic_hash(self) -> str:
        data = self.model_dump(mode="json")
        if sort_states:
            data["states"] = sorted(data["states"])
        if sort_transitions:
            data["transitions"] = sorted(data["transitions"], key=lambda x: x["id"])
        for t in data["transitions"]:
            for key in ("guards", "required_effects", "forbidden_effects"):
                if sort_guards:
                    t[key] = sorted(t[key])
            for key in drop:
                t.pop(key, None)
        for key in drop:
            data.pop(key, None)
        return fingerprint(data)
    return property(semantic_hash)


HASH_MUTANTS = {
    "order_sensitive_guards": (hash_variant(sort_guards=False), hashing.test_hash_invariant_under_reordering),
    "order_sensitive_states": (hash_variant(sort_states=False), hashing.test_hash_invariant_under_reordering),
    "order_sensitive_transitions": (hash_variant(sort_transitions=False), hashing.test_hash_invariant_under_reordering),
    "ignores_forbidden_effects": (hash_variant(drop=("forbidden_effects",)), hashing.test_every_semantic_edit_changes_the_hash),
    "ignores_role": (hash_variant(drop=("role",)), hashing.test_every_semantic_edit_changes_the_hash),
    "ignores_initial_state": (hash_variant(drop=("initial_state",)), hashing.test_every_semantic_edit_changes_the_hash),
    "ignores_transition_id": (hash_variant(drop=("id",)), hashing.test_hash_equality_coincides_with_semantic_equality),
}


@pytest.mark.parametrize("name", sorted(HASH_MUTANTS))
def test_hash_properties_detect_mutant(name, monkeypatch):
    broken, prop = HASH_MUTANTS[name]
    monkeypatch.setattr(Workflow, "semantic_hash", broken)
    with pytest.raises(AssertionError), falsification_only(prop):
        prop()


# --- closure mutants ---------------------------------------------------------------------------------


def closure_variant(*, depth_cap=None, budget_slack=0, always_complete=False, frontier_all_queue=False):
    def closure(graph, roots, budget=None):
        if budget is not None and budget < 0:
            raise ValueError("Negative traversal budget")
        queue, visited = deque((r, 0) for r in sorted(set(roots))), set()
        while queue:
            if budget is not None and len(visited) >= budget + budget_slack:
                frontier = sorted({n for n, _ in queue} if frontier_all_queue else {n for n, _ in queue} - visited)
                return {"affected": sorted(visited), "complete": always_complete or not frontier, "frontier": frontier}
            node, depth = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            if depth_cap is None or depth < depth_cap:
                queue.extend((n, depth + 1) for n in sorted(graph.get(node, [])) if n not in visited)
        return {"affected": sorted(visited), "complete": True, "frontier": []}
    return closure


CLOSURE_MUTANTS = {
    "silent_depth_cap": (closure_variant(depth_cap=2), impact.test_closure_is_reachability),
    "budget_off_by_one": (closure_variant(budget_slack=1), impact.test_budget_reports_a_correct_frontier),
    "always_complete": (closure_variant(always_complete=True), impact.test_budget_reports_a_correct_frontier),
    "frontier_includes_visited": (closure_variant(frontier_all_queue=True), impact.test_budget_reports_a_correct_frontier),
}


@pytest.mark.parametrize("name", sorted(CLOSURE_MUTANTS))
def test_closure_properties_detect_mutant(name, monkeypatch):
    broken, prop = CLOSURE_MUTANTS[name]
    monkeypatch.setattr(impact, "closure", broken)
    with pytest.raises(AssertionError), falsification_only(prop):
        prop()


def test_closure_control_installs_the_real_function():
    assert impact.closure is real_closure
    assert closure_variant()({"a": ["b"], "b": ["a"]}, ["a"]) == real_closure({"a": ["b"], "b": ["a"]}, ["a"])


# --- receipt mutants ---------------------------------------------------------------------------------


def skips_artifact_hash(receipt, subject, claim, kind):
    forged = copy.deepcopy(receipt)
    if isinstance(forged.get("artifact"), dict):
        forged["artifact_hash"] = fingerprint(forged["artifact"])
    return real_assess(forged, subject, claim, kind)


def trusts_the_matrix_verdict(receipt, subject, claim, kind):
    """Believes the receipt's own cells: treats every actual observation as equal to the expected one."""
    forged = copy.deepcopy(receipt)
    for cell in forged.get("artifact", {}).get("cells", []):
        if isinstance(cell, dict) and isinstance(cell.get("expected"), dict):
            cell["actual"] = copy.deepcopy(cell["expected"])
    forged["artifact_hash"] = fingerprint(forged.get("artifact"))
    return real_assess(forged, subject, claim, kind)


def ignores_subject(receipt, subject, claim, kind):
    return real_assess(receipt, receipt.get("subject", subject), claim, kind)


RECEIPT_MUTANTS = {
    "skips_artifact_hash": (skips_artifact_hash, receipts.test_resealed_mutation_is_caught_by_artifact_hash_or_subject),
    "trusts_the_matrix_verdict": (trusts_the_matrix_verdict, receipts.test_flipping_one_observed_result_is_a_recomputed_failure),
    "ignores_subject": (ignores_subject, receipts.test_stale_subject_dimension_makes_receipt_stale),
}


@pytest.mark.parametrize("name", sorted(RECEIPT_MUTANTS))
def test_receipt_properties_detect_mutant(name, monkeypatch):
    broken, prop = RECEIPT_MUTANTS[name]
    genuine = receipts.build_genuine()
    monkeypatch.setattr(receipts, "assess_receipt", broken)
    with pytest.raises(AssertionError), falsification_only(prop):
        prop(genuine=genuine)


# --- contract mutants --------------------------------------------------------------------------------


REAL_LOAD = contracts.load


def relaxed_length(name: str) -> dict:
    schema = REAL_LOAD(name)
    del schema["properties"]["actor_id"]["maxLength"]
    return schema


def tightened_enum(name: str) -> dict:
    schema = REAL_LOAD(name)
    schema["properties"]["rejection_source"]["enum"] = ["Recommended"]
    return schema


def test_schema_relaxed_beyond_the_model_is_detected(monkeypatch):
    """A published schema that forgot a bound accepts instances the model refuses. Found by the near-miss
    (stretched string) comparison; schema-side generation alone would rarely exceed the missing bound."""
    monkeypatch.setattr(contracts, "load", lambda n: relaxed_length(n) if n == "execute-command" else REAL_LOAD(n))
    with pytest.raises(AssertionError):
        contracts.test_mutations_are_refused_by_both_or_neither("execute-command")


def test_schema_tighter_than_the_model_is_detected(monkeypatch):
    """A published schema stricter than the model rejects instances the model itself produces."""
    monkeypatch.setattr(contracts, "load", lambda n: tightened_enum(n) if n == "semantic-transaction" else REAL_LOAD(n))
    with pytest.raises(AssertionError):
        contracts.test_instances_the_model_builds_are_schema_valid("semantic-transaction")
