"""PO-M1..M6 (metamodel, rules), PO-L1 (lens law checker), PO-D6 (harness sensitivity)."""
from __future__ import annotations

import json
import random

import pytest
from eijaref import asp, catalogue, lens, metamodel, rules

from conftest import ROOT, load_bench

bench = load_bench()


# ---- rules IR -----------------------------------------------------------------------------------------------

@pytest.mark.parametrize("text", ["R1: p(X) :- q(X), not p(X).", "R1: p(X) :- q(X), not r(X).\nR2: r(X) :- q(X), not p(X)."])
def test_po_m3_negation_inside_recursion_is_rejected(text) -> None:
    with pytest.raises(rules.RuleError):
        rules.stratify(rules.parse(text))


@pytest.mark.parametrize("text", ["R1: p(X, Y) :- q(X).", "R1: p(X) :- q(X), not r(Y).", "R1: p(X) :- q(X), neq(X, Y)."])
def test_po_m3_unsafe_rules_are_rejected(text) -> None:
    with pytest.raises(rules.RuleError):
        rules.stratify(rules.parse(text))


def test_po_m3_strata_put_negated_relations_strictly_below_their_readers() -> None:
    prog = rules.parse("R1: a(X) :- base(X).\nR2: b(X) :- base(X), not a(X).\nR3: c(X) :- base(X), not b(X).")
    s = rules.stratify(prog)
    assert s["a"] < s["b"] < s["c"] and s["base"] == 0


def test_po_m5_reference_and_sqlite_agree_on_all_pilot_programs() -> None:
    r = bench.f5_rules(samples=60)
    for name, d in r["differential"].items():
        assert d["mismatches_reference_vs_sqlite"] == 0, name
        assert d["fact_sets_where_a_final_head_is_non_empty"] > 10, name  # the differential is not vacuous
    assert all(r["loader_rejects"].values())


def test_po_m6_a_limit_inside_the_recursive_query_truncates_silently_and_the_probe_detects_it() -> None:
    g = bench.f5_rules(samples=1)["recursion_guard"]
    assert g["true_reach_size"] == 51 and g["count_with_limit_inside_the_recursive_select"] == 10
    assert g["detect_truncation_by_asking_for_limit_plus_one"] is True


def test_po_m6_stratified_evaluation_terminates_and_is_monotone_for_positive_programs() -> None:
    prog = rules.parse("R1: reach(X, Y) :- edge(X, Y).\nR2: reach(X, Z) :- reach(X, Y), edge(Y, Z).")
    rng = random.Random(8)
    for _ in range(200):
        nodes = "abcdef"
        e1 = {(rng.choice(nodes), rng.choice(nodes)) for _ in range(rng.randrange(0, 12))}
        e2 = e1 | {(rng.choice(nodes), rng.choice(nodes))}
        r1 = rules.evaluate(prog, {"edge": e1}).get("reach", set())
        r2 = rules.evaluate(prog, {"edge": e2}).get("reach", set())
        assert r1 <= r2  # adding facts never removes a positive consequence: the polarity claim the loader must guard


def test_po_m5_negation_is_not_monotone_which_is_why_it_needs_a_completeness_guard() -> None:
    prog = rules.parse("R1: verified(R) :- verifies(T, R).\nR2: violation(R) :- requirement(R), not verified(R).")
    few = rules.evaluate(prog, {"requirement": {("r",)}}).get("violation", set())
    more = rules.evaluate(prog, {"requirement": {("r",)}, "verifies": {("t", "r")}}).get("violation", set())
    assert few == {("r",)} and more == set()  # more facts, fewer findings: the reason ADR-0095 has the closed-world guard


@pytest.mark.skipif(not asp.available(), reason="NOT_RUN: clingo is not installed")
def test_po_m4_clingo_agrees_with_the_reference_and_its_fixtures_replay() -> None:
    r = bench.f5b_asp_bridge(samples=40)
    assert all(d["mismatches_reference_vs_clingo"] == 0 for d in r["differential"].values())
    assert all(f["replayed_in_reference_and_sqlite"] for f in r["synthesised_positive_fixtures"].values())
    assert r["dead_rule_control_returns_none"] is True


# ---- metamodel and catalogue (files owned by the metamodel and rules aspects) -----------------------------

def _load(rel):
    p = ROOT / rel
    if not p.is_file():
        pytest.skip(f"NOT_RUN: {rel} missing")
    return json.loads(p.read_text(encoding="utf-8"))


def test_po_m1_metamodel_tables_have_no_isolated_type_unmeetable_obligation_or_dangling_rule_id() -> None:
    mm, cat = _load("graph/schema/metamodel.json"), _load("graph/rules/catalogue.json")
    assert metamodel.check_tables(mm, {r["id"] for r in cat["rules"]}) == []


def test_po_m2_constructive_instance_inhabits_every_type_and_meets_every_minimum_obligation() -> None:
    mm = _load("graph/schema/metamodel.json")
    nodes, edges = metamodel.constructive_instance(mm)
    assert len(nodes) == len(mm["node_types"]) and edges
    assert metamodel.check_instance(mm, nodes, edges, with_min_obligations=True) == set()


def test_po_m2_the_instance_checker_has_teeth() -> None:
    mm = _load("graph/schema/metamodel.json")
    nodes, edges = metamodel.constructive_instance(mm)
    missing = metamodel.check_instance(mm, nodes, [], with_min_obligations=True)
    assert any(c == "obligation-unmet" for c, _ in missing)  # dropping every edge breaks the minimum obligations
    a, b = nodes[0]["id"], nodes[1]["id"]
    bad = metamodel.check_instance(mm, nodes, [{"kind": "contains", "from": a, "to": a}])
    assert ("self-loop", f"contains|{a}|{a}|") in bad
    cyc = [{"kind": "supersedes", "from": "repo://docs/adr/0001-x.md", "to": "repo://docs/adr/0002-y.md"},
           {"kind": "supersedes", "from": "repo://docs/adr/0002-y.md", "to": "repo://docs/adr/0001-x.md"}]
    typed = [{"id": e, "type": "adr"} for e in ("repo://docs/adr/0001-x.md", "repo://docs/adr/0002-y.md")]
    assert ("link-kind-cycle", "supersedes") in metamodel.check_instance(mm, typed, cyc)


def test_po_m1_the_metamodel_check_finds_real_defects_in_a_synthetic_metamodel() -> None:
    mm = {"node_types": {"a": {"example": "x"}, "b": {"example": "y"}, "c": {"example": "z"}}, "supertypes": {},
          "domain_tags": [{"tag": "t"}, {"tag": "t"}],
          "link_types": {"k": {"acyclic": False, "signatures": [{"from": ["a"], "to": ["b"], "max_in": 0,
                                                                 "obligations": [{"min": 1, "rule": "WV-999", "scope": "b", "side": "in"},
                                                                                 {"min": 1, "rule": "WV-001", "scope": "c", "side": "in"}]}]}}}
    codes = {c for c, _ in metamodel.check_tables(mm, {"WV-001"})}
    assert {"MM-004", "MM-020", "MM-021", "MM-022", "MM-025"} <= codes


def test_po_m3_catalogue_strata_are_recomputed_identically_and_the_catalogue_is_stratifiable() -> None:
    cat = _load("graph/rules/catalogue.json")
    rec = catalogue.recompute(cat)
    assert rec["rules"] == len(cat["rules"]) and rec["problems"] == []
    assert catalogue.stratify_catalogue(cat)


def test_po_m3_a_wrong_declared_stratum_and_a_negative_read_at_the_same_stratum_are_caught() -> None:
    cat = json.loads(json.dumps(_load("graph/rules/catalogue.json")))
    victim = next(r for r in cat["rules"] if (r["reads"] or {}).get("neg"))
    victim["stratum"] = 0
    assert catalogue.recompute(cat)["problems"]


def test_po_m3_negation_through_the_finding_relation_is_stratifiable_only_because_stratum_3_feeds_finding3() -> None:
    cat = json.loads(json.dumps(_load("graph/rules/catalogue.json")))
    prog = catalogue.as_program(cat)
    assert rules.stratify(prog)
    # The control: if a stratum-3 rule fed `finding` itself, the catalogue would be unstratifiable.
    loop = [r for r in prog if r.head.pred == "r_finding3"]
    cyc = [rules.Rule(r.id, rules.Atom("r_finding", r.head.terms), r.body) if r.head.pred == "r_finding3" else r for r in prog]
    assert loop
    with pytest.raises(rules.RuleError):
        rules.stratify(cyc)


# ---- lens laws ----------------------------------------------------------------------------------------------

def test_po_l1_law_checker_reproduces_the_papers_three_counterexamples() -> None:
    controls = lens.run_paper_controls()
    assert all(c["agrees"] for c in controls.values()), controls
    assert {n: c["violated"] for n, c in controls.items()} == {
        "getput_not_putget": ["PutGet"], "putget_not_getput": ["GetPut"], "well_behaved_not_putput": ["PutPut"]}


def test_po_l1_identity_and_constant_view_lenses_satisfy_the_laws_they_should() -> None:
    srcs = (0, 1, 2)
    ident = lens.check_lens_laws(srcs, srcs, lambda c: c, lambda a, c: a)
    assert all(not v for v in ident.values())  # the identity lens is very well behaved
    const = lens.check_lens_laws(srcs, (0,), lambda c: 0, lambda a, c: c)
    assert not const["GetPut"] and not const["PutPut"]


def test_po_l1_a_partial_put_is_checked_only_where_it_accepts() -> None:
    def put(a, c):
        return lens.REJECTED if a < 0 else a
    bad = lens.check_lens_laws((0, 1), (0, 1, -1), lambda c: c, put)
    assert not any(bad.values())  # rejection is not a violation; a lens may refuse


# ---- determinism harness sensitivity ---------------------------------------------------------------------------

def test_po_d6_the_seed_matrix_sees_a_seeded_set_iteration_defect_and_passes_the_sorted_pipeline() -> None:
    r = bench.f8_harness_sensitivity(seeds=(0, 1, 2, 3, 4, 5))
    if r["status"] == "NOT_RUN":
        pytest.skip(r["reason"])
    assert r["distinct_outputs_iterating_a_set"] > 1 and r["distinct_outputs_sorted"] == 1
    assert r["harness_detects_the_seeded_defect"] is True
