"""Oracles for docs/weave/research/math-and-cs-foundations.md.

These assert the measured facts the dossier relies on. A missing optional package gives a skip, which
is the pytest spelling of NOT_RUN; it is never a pass.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

BENCH = Path(__file__).resolve().parents[2] / "graph" / "bench" / "foundations_checks.py"
spec = importlib.util.spec_from_file_location("foundations_checks", BENCH)
checks = importlib.util.module_from_spec(spec)
sys.modules["foundations_checks"] = checks
spec.loader.exec_module(checks)


def test_status_lattice_is_compositional_but_kernel_aggregate_is_not() -> None:
    r = checks.status_lattice()
    assert r["status"] == "MEASURED"
    assert r["kernel_aggregate_order_independent"] is True
    assert r["lub_semilattice_laws"] == {"commutative": True, "idempotent": True, "associative": True}
    assert r["lub_fold_equals_kernel_aggregate_on_flat_inputs"] is True
    assert r["lub_rollup_composes"] is True
    # The kernel is correct on flat receipt lists; re-aggregating aggregates loses CONFLICT.
    assert r["hierarchical_counterexample"] == {"flat": "CONFLICT", "rolled_up": "FAIL"}
    assert r["kernel_conflict_is_absorbing"] is False


def test_impact_closure_agrees_with_recursive_cte() -> None:
    r = checks.closure_vs_recursive_cte(graphs=60)
    assert r["status"] == "MEASURED" and r["mismatches"] == 0


def test_report_is_byte_identical_between_runs() -> None:
    a = checks.status_lattice()
    b = checks.status_lattice()
    assert a == b


@pytest.mark.skipif(checks.nx is None, reason="networkx not installed (NOT_RUN)")
def test_deterministic_graph_recipes_are_stable_and_library_defaults_are_not() -> None:
    r = checks.graph_order_sensitivity(trials=60)["distinct_outputs"]
    assert r["sorted SCC member tuples"] == 1
    assert r["nx.lexicographical_topological_sort"] == 1
    assert r["nx.condensation labels"] > 1  # component numbering follows insertion order


@pytest.mark.skipif(checks.nx is None, reason="networkx not installed (NOT_RUN)")
def test_pagerank_needs_quantising_before_it_is_an_artefact() -> None:
    r = checks.pagerank_float_determinism(shuffles=8)
    assert r["distinct_after_round_1e-10"] == 1
    assert r["distinct_top20_id_orders"] == 1


@pytest.mark.skipif(checks.rfc8785 is None, reason="rfc8785 not installed (NOT_RUN)")
def test_kernel_canonical_json_is_not_rfc8785() -> None:
    r = checks.jcs_vs_kernel_canonical()
    assert {"float_1.0", "float_neg_zero", "key_order_astral_vs_bmp", "int_2**60"} <= set(r["differs"])
