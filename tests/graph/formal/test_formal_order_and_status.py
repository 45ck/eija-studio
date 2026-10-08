"""PO-G3, PO-G4 (canonical SCC labels and lexicographic topological order) and PO-S1..S6 (status algebras)."""
from __future__ import annotations

import itertools
import random

import pytest
from eijaref import order, status, suites

from weave_formal_support import load_bench

bench = load_bench()


@pytest.fixture(scope="module")
def f2() -> dict:
    return bench.f2_status()  # ~14 s on the reference PC: computed once per module


@pytest.fixture(scope="module")
def f4() -> dict:
    return bench.f4_order(n=4, n_lab=3)  # ~7 s: all 65536 digraphs on 4 nodes, all 13824 labelings on 3 nodes


# ---- order -------------------------------------------------------------------------------------------------

def test_po_g3_scc_labels_are_accepted_by_the_checker_and_equal_the_definition_on_every_4_node_graph(f4) -> None:
    r = f4
    assert r["graphs"] == 65536
    assert r["producer_labels_accepted_by_checker"] == 65536
    assert r["producer_labels_different_from_mutual_reachability_definition"] == 0


def test_po_g3_checker_accepts_exactly_the_canonical_labelling_of_every_3_node_graph(f4) -> None:
    r = f4
    assert r["labelings_tried_on_3_nodes"] == 13824
    assert r["checker_disagrees_with_definition"] == 0


def test_po_g4_topological_order_is_the_brute_force_lexicographic_minimum_and_is_accepted(f4) -> None:
    r = f4
    assert r["acyclic_among_them"] == 543  # the number of labelled DAGs on 4 nodes: the enumeration is complete
    assert r["producer_order_differs_from_brute_force_lexicographic_minimum"] == 0
    assert r["checker_accepts_producer_order"] == 543


def test_po_g3_g4_suite_passes_on_the_reference_and_fails_on_an_insertion_order_dependent_labelling() -> None:
    assert suites.suite_order(order.scc_labels, order.lexicographic_topological_order, n=3) == []
    bad = suites.suite_order(suites.wrong_scc_nx_style, order.lexicographic_topological_order, n=3)
    assert bad != []


def test_po_g3_networkx_condensation_labels_are_valid_partitions_but_not_canonical() -> None:
    nx = pytest.importorskip("networkx")
    del nx
    r = bench.f4b_library_defaults(trials=40)
    assert r["distinct_min_member_labellings"] == 1
    assert r["distinct_nx_condensation_labellings"] > 1
    assert r["checker_accepts_nx_partition_after_min_member_relabel"] == 40


# ---- status ------------------------------------------------------------------------------------------------

def test_po_s1_join_laws_hold_over_all_pairs_and_216_triples() -> None:
    assert status.check_laws() == {"commutative": True, "associative": True, "idempotent": True, "identity_not_run": True}


def test_po_s1_join_is_a_function_of_the_set_for_every_list_length_up_to_6() -> None:
    """The finite reduction: commutative + associative + idempotent means the fold ignores order and repeats."""
    rng = random.Random(1)
    for _ in range(500):
        xs = [rng.choice(status.VALUES) for _ in range(rng.randrange(0, 7))]
        ys = xs[:]
        rng.shuffle(ys)
        assert status.join(xs) == status.join(ys) == status.join(sorted(set(xs)))


def test_po_s4_join_equals_the_kernel_aggregate_on_every_flat_list_up_to_length_6(f2) -> None:
    r = f2
    if not r["kernel_present"]:
        pytest.skip("kernel not importable: NOT_RUN")
    assert r["join_equals_kernel_aggregate_on_flat_inputs"] is True


def test_po_s4_kernel_rollup_defect_is_reproduced_and_the_join_composes() -> None:
    evidence = pytest.importorskip("eija_studio.domain.evidence")
    del evidence
    agg = bench._kernel_aggregate
    assert agg(["PASS", "FAIL", "FAIL"]) == "CONFLICT"
    assert agg([agg(["PASS", "FAIL"]), "FAIL"]) == "FAIL"  # the kernel does not compose (needs its own ADR)
    flat = status.join(["PASS", "FAIL", "FAIL"])
    rolled = status.join([status.join(["PASS", "FAIL"]), "FAIL"])
    assert flat == rolled == "CONFLICT"


def test_po_s2_gate_is_pass_iff_every_input_is_pass_under_all_120_chains(f2) -> None:
    r = f2
    assert r["chains"] == 120
    assert r["gate_is_pass_iff_all_pass_violations_over_all_chains"] == 0


def test_po_s2_not_run_absorbs_pass_and_the_empty_gate_is_not_run() -> None:
    for chain in status.all_chains():
        assert status.meet(["PASS", "NOT_RUN"], chain) != "PASS"
        assert status.meet([], chain) == "NOT_RUN"


def test_po_s3_a_required_check_without_evidence_can_never_pass_a_claim(f2) -> None:
    r = f2
    assert r["two_level_pass_iff_every_check_joins_to_pass_violations"] == 0
    assert r["two_level_cases"] == 64 + 64 ** 2 + 64 ** 3
    assert status.claim_status([["PASS"], []]) == "NOT_RUN"
    assert status.join(["PASS", "NOT_RUN"]) == "PASS"  # correct for ALTERNATIVE evidence, wrong for a required check


def test_po_s_suite_passes_reference_and_catches_the_vacuous_and_leaky_implementations() -> None:
    assert suites.suite_status(status.join, status.meet, status.claim_status) == []
    assert suites.suite_status(status.join, suites.wrong_status_vacuous, status.claim_status) != []
    assert suites.suite_status(status.join, status.leaky_meet, status.claim_status) != []


def test_po_s6_only_covered_lifts_to_pass() -> None:
    assert [s for s, v in status.LIFT.items() if v == "PASS"] == ["COVERED"]
    assert set(status.LIFT) == set(status.LINK_STATUSES)
    for chain in status.all_chains():
        for combo in itertools.product(status.LINK_STATUSES, repeat=2):
            assert (status.lifted_gate(combo, chain) == "PASS") == all(s == "COVERED" for s in combo)


def test_po_s5_link_status_laws_pass_on_the_reference_and_catch_three_wrong_implementations() -> None:
    assert suites.suite_link_status(suites.link_status_ref) == []
    assert suites.suite_link_status(suites.wrong_link_status_any_ack) != []
    assert suites.suite_link_status(suites.wrong_link_status_unresolved_covered) != []

    def ack_clears_orphan(baseline, observation, acks, link_id):
        return "COVERED" if observation == "ABSENT" and acks else suites.link_status_ref(baseline, observation, acks, link_id)

    assert suites.suite_link_status(ack_clears_orphan) != []
