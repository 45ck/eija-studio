"""PO-G1, PO-G2, PO-G5, PO-G6: impact closure against independent references and a certificate checker.

Each test states its domain; a pass is a MEASUREMENT on that domain, not a proof (the theorem is proven on paper
in docs/weave/design/formal-verification-of-weave.md section 5).
"""
from __future__ import annotations

import random
import sqlite3

import pytest
from eijaref import closure, suites

from conftest import load_bench

bench = load_bench()


def test_po_g1_kernel_closure_equals_two_independent_references_on_every_3_node_graph() -> None:
    kernel = pytest.importorskip("eija_studio.domain.impact").closure
    assert suites.suite_closure(lambda g, r: kernel(g, r)["affected"], n=3) == []
    assert suites.suite_closure(closure.warshall_closure, n=3) == []


def test_po_g1_suite_has_teeth_it_rejects_a_one_hop_closure() -> None:
    assert suites.suite_closure(suites.wrong_closure_one_hop, n=3) != []


def test_po_g1_bfs_certificate_is_accepted_and_equals_the_reference_on_every_3_node_graph() -> None:
    for nodes, edges in bench._digraphs(3):
        g, edge_s = bench._adj(nodes, edges), frozenset(edges)
        for roots in bench._subsets(nodes):
            cert = closure.certify(g, roots)
            assert closure.check_certificate(edge_s, roots, cert) == (True, "accepted")
            assert cert["C"] == closure.lfp_kleene(g, roots)
            for t in nodes:
                if t not in cert["C"]:
                    assert closure.check_unreachable(edge_s, roots, cert["C"], t)[0]


def test_po_g2_checker_accepts_only_true_closures_exhaustive_at_2_nodes() -> None:
    r = bench.f1c_checker_soundness_and_mutants(n_exh=2, n_mut=2, samples=3000)
    assert r["real_checker_exhaustive"]["accepted_but_not_closure"] == 0
    assert r["real_checker_exhaustive"]["accepted"] > 0  # the checker is not vacuously rejecting everything
    assert r["real_checker_perturbed_sample"]["accepted_but_not_closure"] == 0


def test_po_g2_every_condition_of_the_checker_is_necessary() -> None:
    """Negative controls on the checker itself: dropping any one of a, b1, b2, b3, c admits a wrong closure."""
    r = bench.f1c_checker_soundness_and_mutants(n_exh=1, n_mut=3, samples=10)
    assert r["mutants_with_counterexample"] == {"a": True, "b1": True, "b2": True, "b3": True, "c": True}


def test_po_g2_a_rank_cycle_or_a_fake_parent_is_rejected() -> None:
    edges = frozenset({("a", "b")})
    good = closure.certify({"a": ["b"]}, ["a"])
    assert closure.check_certificate(edges, ["a"], good)[0]
    forged = {"C": frozenset({"a", "b", "c"}), "rank": {"a": 0, "b": 1, "c": 1}, "parent": {"b": "a", "c": "a"}}
    assert closure.check_certificate(edges, ["a"], forged) == (False, "b1:parent-edge-missing")
    cyc = {"C": frozenset({"b", "c"}), "rank": {"b": 1, "c": 1}, "parent": {"b": "c", "c": "b"}}
    assert closure.check_certificate(frozenset({("b", "c"), ("c", "b")}), [], cyc)[0] is False


def test_po_g5_kernel_budgeted_closure_is_a_subset_and_complete_means_equal() -> None:
    r = bench.f1b_budget_semantics(n=2)
    if r["status"] == "NOT_RUN":
        pytest.skip(r["reason"])
    assert r["affected_not_subset_of_closure"] == r["complete_but_not_equal_to_closure"] == r["frontier_not_in_closure"] == 0


def test_po_g6_sqlite_recursive_union_equals_the_reference_on_every_3_node_graph() -> None:
    r = bench.f1_closure(n_big=2, n_sql=3)
    assert r["sqlite_cte"]["mismatches"] == 0 and r["sqlite_cte"]["cases"] == 4096


def test_po_g6_a_limit_inside_the_recursive_select_truncates_silently() -> None:
    """The guard must detect truncation (ask for LIMIT + 1); a bare LIMIT would hide a partial closure."""
    db = sqlite3.connect(":memory:")
    db.execute("create table e(a, b)")
    db.executemany("insert into e values (?, ?)", [(f"n{i:03d}", f"n{i + 1:03d}") for i in range(30)])
    q = "with recursive r(x) as (select 'n000' union select e.b from e join r on e.a = r.x {limit}) select count(*) from r"
    assert db.execute(q.format(limit="")).fetchone()[0] == 31
    assert db.execute(q.format(limit="limit 10")).fetchone()[0] == 10  # silently short
    assert db.execute(q.format(limit="limit 11")).fetchone()[0] == 11  # limit + 1 rows: the guard fires


def test_po_g1_random_larger_graphs_agree_across_all_four_implementations() -> None:
    kernel = pytest.importorskip("eija_studio.domain.impact").closure
    rng = random.Random(21)
    for _ in range(300):
        n = rng.randrange(2, 30)
        nodes = [f"n{i:02d}" for i in range(n)]
        edges = {(rng.choice(nodes), rng.choice(nodes)) for _ in range(rng.randrange(0, 3 * n))}
        g = {x: [] for x in nodes}
        for a, b in sorted(edges):
            g[a].append(b)
        roots = sorted(rng.sample(nodes, min(len(nodes), rng.randrange(1, 4))))
        ref = sorted(closure.lfp_kleene(g, roots))
        assert sorted(closure.warshall_closure(g, roots)) == ref
        assert kernel(g, roots)["affected"] == ref
        cert = closure.certify(g, roots)
        assert closure.check_certificate(frozenset(edges), roots, cert)[0] and sorted(cert["C"]) == ref
