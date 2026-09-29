"""Cross-aspect differential checks: the formal lane's independent references and law suites run against the other
aspects' reference implementations (files under graph/bench, graph/rules, graph/schema).

A sibling file that is missing or does not import gives a skip (NOT_RUN), never a pass. Nothing here edits a
sibling file. Where two independent implementations agree on an exhaustive or seeded domain that is
N-version evidence: it catches a slip in either, and it does not catch a shared misreading of the specification.
"""
from __future__ import annotations

import itertools
import json
import random

import pytest
from eijaref import canon, closure, order, status, suites

from conftest import ROOT, load_bench

bench = load_bench()


def sibling(name: str, rel: str):
    module = bench._load_path(name, ROOT / rel)
    if module is None:
        pytest.skip(f"NOT_RUN: {rel} is missing or does not import")
    return module


@pytest.fixture(scope="module")
def impact():
    return sibling("weave_impact_math_reference", "graph/bench/impact_math_reference.py")


@pytest.fixture(scope="module")
def identity():
    return sibling("weave_identity_checks", "graph/bench/identity_checks.py")


@pytest.fixture(scope="module")
def rules_ref():
    return sibling("weave_rules_reference", "graph/rules/reference.py")


@pytest.fixture(scope="module")
def consistency():
    return sibling("weave_consistency_checks", "graph/bench/consistency_checks.py")


# ---- impact aspect: closure, SCC, order, status ----------------------------------------------------------

def test_x_impact_closure_passes_the_formal_suite_and_its_certificate_is_accepted(impact) -> None:
    assert suites.suite_closure(lambda g, r: impact.closure(g, r)["affected"], n=3) == []
    for nodes, edges in bench._digraphs(3):
        g, edge_s = bench._adj(nodes, edges), frozenset(edges)
        for roots in bench._subsets(nodes):
            rep = impact.closure(g, list(roots))
            cert = {"C": frozenset(rep["affected"]), "rank": rep["distance"],
                    "parent": {k: v for k, v in rep["parent"].items() if v is not None}}
            assert closure.check_certificate(edge_s, roots, cert)[0], (edges, roots)


def test_x_impact_budgeted_closure_is_a_prefix_of_the_true_closure(impact) -> None:
    for nodes, edges in bench._digraphs(3):
        g = bench._adj(nodes, edges)
        for roots in bench._subsets(nodes):
            full = set(closure.lfp_kleene(g, roots))
            for budget in range(5):
                r = impact.closure(g, list(roots), budget)
                assert set(r["affected"]) <= full
                assert not r["complete"] or set(r["affected"]) == full
                assert set(r["frontier"]) <= full


def test_x_impact_scc_labels_and_topological_order_agree_with_the_formal_checkers(impact) -> None:
    for nodes, edges in bench._digraphs(3):
        adj = bench._adj(nodes, edges)
        lab = impact.scc_labels(list(nodes), adj)
        assert order.check_scc_labels(nodes, edges, lab)[0], edges
        _label, _members, dag = impact.condensation(list(nodes), adj)
        topo = impact.lex_topological_order(dag)
        cond_edges = [(a, b) for a, bs in dag.items() for b in bs]
        assert order.check_lexicographic_topological_order(list(dag), cond_edges, topo)[0], edges


def test_x_impact_status_folds_satisfy_the_representation_agnostic_status_suite(impact) -> None:
    def join(values):
        return impact.fold_a(list(values))

    def claim(checks):
        return impact.fold_b([impact.fold_a(list(ev)) for ev in checks])

    assert suites.suite_status(join, lambda v: impact.fold_b(list(v)), claim) == []


def test_x_impact_join_equals_the_formal_join_on_the_kernel_five_and_documents_two_differences(impact) -> None:
    five = suites.KERNEL_FIVE
    for k in range(1, 5):
        for p in itertools.product(five, repeat=k):
            assert impact.fold_a(list(p)) == status.join(p)
    assert impact.fold_a([]) == "UNKNOWN" and status.join([]) == "NOT_RUN"  # representational difference 1
    with pytest.raises(ValueError):
        impact.fold_a(["NOT_RUN"])  # difference 2: NOT_RUN is refused by their join, ignored by ours
    assert status.join(["NOT_RUN", "PASS"]) == "PASS"
    for chain in status.all_chains():
        for k in range(1, 4):
            for p in itertools.product(status.VALUES, repeat=k):
                assert (impact.fold_b(list(p), chain) == "PASS") == all(x == "PASS" for x in p) == (status.meet(p, chain) == "PASS")


# ---- metamodel aspect: canonical writer -----------------------------------------------------------------

def test_x_identity_jcs_writer_equals_the_formal_writer_on_the_hostile_pool_and_random_values(identity) -> None:
    pool = suites._canon_pool()
    for v in pool:
        assert identity.jcs_dumps(v) == canon.dumps(v), v
    rng = random.Random(17)
    alphabet = list("ab\"\\\n€דּ\U0001f600￿\x00\x7f")
    for _ in range(2000):
        keys = ["".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 4))) for _ in range(rng.randrange(0, 5))]
        v = {k: [rng.randrange(-5, 5), "".join(rng.choice(alphabet) for _ in range(3)), None] for k in dict.fromkeys(keys)}
        assert identity.jcs_dumps(v) == canon.dumps(v)


def test_x_identity_writer_accepts_a_tuple_where_the_formal_writer_refuses_it(identity) -> None:
    """Both are deterministic; the difference is a collision class: (1, 2) and [1, 2] give the same bytes."""
    assert identity.jcs_dumps((1, 2)) == identity.jcs_dumps([1, 2])
    with pytest.raises(canon.InvalidValue):
        canon.dumps((1, 2))


def test_x_identity_fast_writer_equals_the_reference_only_without_astral_keys(identity) -> None:
    ascii_doc = {"b": [1, {"z": None, "a": "x\n"}], "a": True}
    assert identity.jcs_dumps_fast(ascii_doc) == identity.jcs_dumps(ascii_doc)
    astral = {"\U00010000": 1, "￿": 2}
    assert identity.jcs_dumps_fast(astral) != identity.jcs_dumps(astral)  # why the fast path is restricted to ASCII keys


def test_x_identity_domain_separated_hash_has_no_collisions_over_tags_and_the_hostile_pool(identity) -> None:
    tags = ["eija.weave.node.v1", "eija.weave.edge.v1", "eija.weave.shard.v1"]
    seen: dict[str, tuple] = {}
    for tag in tags:
        for v in suites._canon_pool():
            h = identity.dhash(tag, v)
            assert seen.setdefault(h, (tag, json.dumps(v, sort_keys=True, default=str))) == (tag, json.dumps(v, sort_keys=True, default=str))


# ---- rules aspect: verdict algebra, exit codes, canonical form -------------------------------------------

def test_x_rules_verdict_fold_is_pass_iff_all_pass_and_the_empty_run_is_not_run(rules_ref) -> None:
    vs = ("PASS", "FAIL", "NOT_RUN")
    for k in range(1, 5):
        for p in itertools.product(vs, repeat=k):
            got = rules_ref.fold_verdicts(p)
            assert (got == "PASS") == all(x == "PASS" for x in p)
            assert (got == "FAIL") == ("FAIL" in p)  # NOT_RUN never hides a FAIL; NOT_RUN absorbs PASS
    assert rules_ref.fold_verdicts([]) == "NOT_RUN"
    assert rules_ref.fold_verdicts(["FAIL", "NOT_RUN"]) == "FAIL"


def test_x_rules_rule_verdict_closed_world_guard_is_exhaustively_correct(rules_ref) -> None:
    """Exhaustive over 3 finding counts x 2 prerequisite states x 3 read effects (none, monotone, unsafe). A finding is
    sound on partial input only when the finding set is monotone in the incomplete relations; a rule that reads an
    incomplete relation negatively (or through a derived relation) is NOT_RUN whatever it found (ADR-0095, audit 2026-09-29)."""
    for findings, prereq, effect in itertools.product((0, 1, 2), (True, False), ("none", "monotone", "unsafe")):
        v = rules_ref.rule_verdict(findings, prereq, effect)
        sound_finding = findings > 0 and prereq and effect != "unsafe"
        assert (v == "FAIL") == sound_finding
        assert (v == "PASS") == (findings == 0 and prereq and effect == "none")
        assert (v == "NOT_RUN") == (not sound_finding and not (findings == 0 and prereq and effect == "none"))


def test_x_rules_exit_code_never_maps_not_run_to_zero_unless_the_acceptance_flag_is_set(rules_ref) -> None:
    assert rules_ref.exit_code("PASS") == 0 and rules_ref.exit_code("FAIL") == 1 and rules_ref.exit_code("NOT_RUN") == 2
    # The acceptance flag turns NOT_RUN into exit 0. That is a policy input an agent could set (design section 7, R-6).
    assert rules_ref.exit_code("NOT_RUN", not_run_accepted=True) == 0
    assert rules_ref.exit_code("FAIL", not_run_accepted=True) == 1


def test_x_rules_canonical_json_equals_the_formal_writer_where_it_accepts_and_refuses_the_rest(rules_ref) -> None:
    """The rules aspect restricts object keys to ASCII identifiers (a stricter domain). Inside it the bytes must be equal;
    outside it the function must refuse, never emit different bytes."""
    accepted = refused = 0
    for v in suites._canon_pool():
        try:
            got = rules_ref.canonical_json(v)
        except ValueError:
            refused += 1
            continue
        accepted += 1
        assert got.encode("utf-8") == canon.dumps(v), v
    assert accepted > 15 and refused >= 1


# ---- consistency aspect: keyed three-way merge -------------------------------------------------------------

def test_x_merge3_laws_hold_exhaustively_on_the_single_key_reduction(consistency) -> None:
    """merge3 is decided key by key from four values (base, ours, theirs, third). Four symbols (absent, a, b, c) realise
    every equality pattern among four slots, so 256 cases stand for every alphabet and every key count."""
    merge3 = consistency.merge3
    vals = (None, "a", "b", "c")

    def rec(v):
        return {} if v is None else {"k": v}

    for b, o, t, u in itertools.product(vals, repeat=4):
        B, O, T, U = map(rec, (b, o, t, u))
        m1, c1 = merge3(B, O, T)
        m2, c2 = merge3(B, T, O)
        assert m1 == m2 and c1 == [{"key": x["key"], "base": x["base"], "ours": x["theirs"], "theirs": x["ours"]} for x in c2]
        assert merge3(B, O, B) == (O, [])
        assert merge3(B, O, O) == (O, [])
        left_i, lc = merge3(B, O, T)
        left = merge3(B, left_i, U) if not lc else None
        right_i, rc = merge3(B, T, U)
        right = merge3(B, O, right_i) if not rc else None
        ldef = left is not None and not left[1]
        rdef = right is not None and not right[1]
        assert ldef == rdef and (not ldef or left[0] == right[0])
        assert ldef == (len({o, t, u} - {b}) <= 1)


def test_x_merge3_is_key_wise_so_the_reduction_is_sound(consistency) -> None:
    merge3 = consistency.merge3
    rng = random.Random(4)
    for _ in range(400):
        keys = [f"k{i}" for i in range(5)]

        def rnd():
            return {k: rng.choice("abc") for k in keys if rng.random() < 0.5}

        b, o, t = rnd(), rnd(), rnd()
        whole, conflicts = merge3(b, o, t)
        for k in keys:
            part, pc = merge3({x: y for x, y in b.items() if x == k}, {x: y for x, y in o.items() if x == k},
                              {x: y for x, y in t.items() if x == k})
            assert ({x: y for x, y in whole.items() if x == k} == part) and ([c for c in conflicts if c["key"] == k] == pc)


def test_x_identity_graph_root_is_a_function_of_the_record_set_and_sees_every_record(identity) -> None:
    """PO-D5 on the metamodel aspect's root definition (two-level: records, then source-file shards)."""
    nodes, edges = identity.synth(40, 90, seed=5)
    base = identity.graph_root(nodes, edges)
    rng = random.Random(12)
    for _ in range(60):
        n2, e2 = nodes[:], edges[:]
        rng.shuffle(n2)
        rng.shuffle(e2)
        n2 = [identity.shuffled(r, rng) for r in n2]
        e2 = [identity.shuffled(r, rng) for r in e2]
        assert identity.graph_root(n2, e2) == base
    for i in range(len(nodes)):  # every single node record is visible in the root
        changed = [dict(n) for n in nodes]
        changed[i] = {**changed[i], "prov": "partial"}
        assert identity.graph_root(changed, edges) != base, i
    for i in range(len(edges)):  # and every single edge record
        assert identity.graph_root(nodes, edges[:i] + edges[i + 1:]) != base, i
    assert identity.graph_root(nodes, edges, view="ui") != base
