"""Oracles for docs/weave/design/impact-ranking-and-confidence.md and graph/schema/math-oracles.md.

Two jobs. (1) Pin every hand-verified worked example (the literal values below are the ones printed in
math-oracles.md). (2) Cross-check the reference implementations against independent oracles: the kernel
(`eija_studio.domain.impact.closure`, `evidence.aggregate_status`), brute force on small instances, exact
rational arithmetic, and networkx when installed (a missing optional package is a skip, which is the
pytest spelling of NOT_RUN, never a pass).

What passes here is a statement about the reference code on the stated domains. It is not a proof for all
inputs; each test says whether it is exhaustive or a seeded sample.
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import os
import random
import sqlite3
import subprocess
import sys
from fractions import Fraction as F
from pathlib import Path
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
_spec = importlib.util.spec_from_file_location("impact_math_reference", ROOT / "graph" / "bench" / "impact_math_reference.py")
m = importlib.util.module_from_spec(_spec)
sys.modules["impact_math_reference"] = m
_spec.loader.exec_module(m)

from eija_studio.domain import evidence as kernel_evidence  # noqa: E402
from eija_studio.domain.impact import closure as kernel_closure  # noqa: E402

try:
    import networkx as nx
except ImportError:  # optional
    nx = None
_HAS_PAGERANK_DEPS = nx is not None and all(importlib.util.find_spec(mod) for mod in ("numpy", "scipy"))  # nx.pagerank imports both lazily

# ---------------------------------------------------------------- worked example G1 (oracle O1)
LINKS = [("S2", "depends_on", "S1"), ("S3", "depends_on", "S2"), ("S1", "depends_on", "S3"),
         ("S2", "satisfies", "R1"), ("T1", "verifies", "R1"), ("S4", "calls", "S3"),
         ("T2", "verifies", "R2"), ("S4", "satisfies", "R2")]
FLOW = {"depends_on": "R", "satisfies": "FR", "verifies": "FR", "calls": "R"}
SOUND = {"depends_on": 1, "satisfies": 0, "verifies": 0, "calls": 2}


def random_graph(seed: int, n_max: int = 14, e_max: int = 40) -> tuple[list[str], m.Adj]:
    rng = random.Random(seed)
    n = rng.randrange(2, n_max)
    names = [f"n{i:02d}" for i in range(n)]
    adj: dict[str, set[str]] = {}
    for _ in range(rng.randrange(0, e_max)):
        adj.setdefault(rng.choice(names), set()).add(rng.choice(names))
    return names, {k: sorted(v) for k, v in sorted(adj.items())}


# ================================================================ O1 closure
def test_o1_tiers_distances_and_witnesses() -> None:
    got = m.tiered_impact(LINKS, FLOW, SOUND, ["S1"])
    assert got == {
        "R1": {"tier": 1, "distance": 2, "witness": ["S1", "S2", "R1"]},
        "R2": {"tier": 2, "distance": 4, "witness": ["S1", "S2", "S3", "S4", "R2"]},
        "S1": {"tier": 0, "distance": 0, "witness": ["S1"]},
        "S2": {"tier": 1, "distance": 1, "witness": ["S1", "S2"]},
        "S3": {"tier": 1, "distance": 2, "witness": ["S1", "S2", "S3"]},
        "S4": {"tier": 2, "distance": 3, "witness": ["S1", "S2", "S3", "S4"]},
        "T1": {"tier": 1, "distance": 3, "witness": ["S1", "S2", "R1", "T1"]},
        "T2": {"tier": 2, "distance": 5, "witness": ["S1", "S2", "S3", "S4", "R2", "T2"]},
    }
    assert "D1" not in got  # an unlinked node is never affected


def test_o1_budget_reports_honest_frontier_and_matches_kernel() -> None:
    g2 = m.arcs_for_tier(LINKS, FLOW, SOUND, 2)
    mine = m.closure(g2, ["S1"], budget=4)
    assert (mine["affected"], mine["complete"], mine["frontier"]) == (["R1", "S1", "S2", "S3"], False, ["S4", "T1"])
    assert mine["order"] == ["S1", "S2", "R1", "S3"]
    ker = kernel_closure(g2, ["S1"], 4)
    assert (mine["affected"], mine["complete"], mine["frontier"]) == (ker["affected"], ker["complete"], ker["frontier"])


def test_o1_deleted_link_still_reaches_dependents_through_union_graph() -> None:
    base = [("S4", "satisfies", "R2"), ("T2", "verifies", "R2")]
    head = [("S4", "satisfies", "R2")]  # the verifies link was deleted in the change
    flow, snd = FLOW, SOUND
    b = m.closure(m.arcs_for_tier(base, flow, snd, 0), ["S4"])["affected"]
    h = m.closure(m.arcs_for_tier(head, flow, snd, 0), ["S4"])["affected"]
    u = m.closure(m.arcs_for_tier(base + head, flow, snd, 0), ["S4"])["affected"]
    assert (b, h, u) == (["R2", "S4", "T2"], ["R2", "S4"], ["R2", "S4", "T2"])


def test_closure_equals_kernel_on_300_seeded_graphs_with_and_without_budget() -> None:
    for seed in range(300):
        names, adj = random_graph(seed)
        rng = random.Random(seed + 1000)
        roots = sorted({rng.choice(names) for _ in range(rng.randrange(1, 4))})
        for budget in (None, 0, 1, 3, 7):
            mine, ker = m.closure(adj, roots, budget), kernel_closure(adj, roots, budget)
            assert (mine["affected"], mine["complete"], mine["frontier"]) == (ker["affected"], ker["complete"], ker["frontier"])


def test_closure_is_the_least_fixed_point_exhaustively_on_tiny_graphs() -> None:
    """Knaster-Tarski/Kleene shape: closure = F(closure), and it is contained in every set S with F(S) <= S."""
    for seed in range(60):
        names, adj = random_graph(seed, n_max=8, e_max=14)
        rng = random.Random(seed)
        roots = sorted({rng.choice(names)})
        result = set(m.closure(adj, roots)["affected"])
        succ = lambda x: {v for u in x for v in adj.get(u, [])}  # noqa: E731
        assert result == set(roots) | succ(result)
        for bits in range(1 << len(names)):
            s = {n for i, n in enumerate(names) if bits >> i & 1}
            if set(roots) | succ(s) <= s:
                assert result <= s


def test_closure_is_monotone_in_roots_and_arcs_and_order_independent() -> None:
    for seed in range(100):
        names, adj = random_graph(seed)
        rng = random.Random(seed)
        r1 = sorted({rng.choice(names)})
        r2 = sorted(set(r1) | {rng.choice(names)})
        assert set(m.closure(adj, r1)["affected"]) <= set(m.closure(adj, r2)["affected"])
        more = {k: sorted(set(v) | {rng.choice(names)}) for k, v in adj.items()}
        assert set(m.closure(adj, r1)["affected"]) <= set(m.closure(more, r1)["affected"])
        shuffled = {k: rng.sample(v, len(v)) for k, v in sorted(adj.items(), key=lambda kv: rng.random())}
        assert m.closure(shuffled, r2) == m.closure(adj, r2)


def test_witness_is_the_lexicographically_smallest_shortest_path() -> None:
    for seed in range(100):
        names, adj = random_graph(seed, n_max=9, e_max=25)
        roots = [names[0]]
        rep = m.closure(adj, roots)
        for node in rep["affected"]:
            best = None
            stack = [[names[0]]]
            while stack:
                path = stack.pop()
                if path[-1] == node:
                    if best is None or (len(path), path) < (len(best), best):
                        best = path
                    continue
                if len(path) > 9:
                    continue
                for nxt in adj.get(path[-1], []):
                    if nxt not in path:
                        stack.append([*path, nxt])
            assert m.witness(rep, node) == best


FLOW_TABLE_SQL = "CREATE TABLE flow(type TEXT PRIMARY KEY, f INTEGER NOT NULL, r INTEGER NOT NULL) WITHOUT ROWID"
ARC_VIEW_SQL = """
CREATE VIEW arc AS
SELECT e.src AS src, e.dst AS dst,
       CASE e.soundness WHEN 'must' THEN 0 WHEN 'may' THEN 1 ELSE 2 END AS cls
  FROM edge e JOIN flow x ON x.type = e.type WHERE x.f = 1
UNION
SELECT e.dst, e.src,
       CASE e.soundness WHEN 'must' THEN 0 WHEN 'may' THEN 1 ELSE 2 END
  FROM edge e JOIN flow x ON x.type = e.type WHERE x.r = 1
"""
CLOSURE_SQL = """
WITH RECURSIVE reach(node) AS (
  SELECT node FROM root
  UNION
  SELECT a.dst FROM arc a JOIN reach r ON a.src = r.node WHERE a.cls <= :tier
) SELECT node FROM reach ORDER BY node
"""


def test_o1_sql_view_and_recursive_cte_agree_with_the_reference_at_every_tier() -> None:
    """Against the store aspect's edge table (docs/weave/design/storage-and-query.md section 4.2): text
    soundness on each edge, plus a small generated flow table (derived from the metamodel)."""
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE edge(src TEXT NOT NULL, type TEXT NOT NULL, dst TEXT NOT NULL, origin TEXT NOT NULL, "
               "soundness TEXT NOT NULL, method TEXT NOT NULL, digest TEXT NOT NULL, PRIMARY KEY(src, type, dst)) WITHOUT ROWID")
    db.execute(FLOW_TABLE_SQL)
    db.execute("CREATE TABLE root(node TEXT)")
    names = {0: "must", 1: "may", 2: "heuristic"}
    db.executemany("INSERT INTO edge VALUES (?,?,?,?,?,?,?)",
                   [(s, t, d, "derived", names[SOUND[t]], "none", "") for s, t, d in sorted(LINKS)])
    db.executemany("INSERT INTO flow VALUES (?,?,?)", [(t, int("F" in FLOW[t]), int("R" in FLOW[t])) for t in sorted(FLOW)])
    db.execute("INSERT INTO root VALUES ('S1')")
    db.execute(ARC_VIEW_SQL)
    for tier in (0, 1, 2):
        sql = [n for (n,) in db.execute(CLOSURE_SQL, {"tier": tier})]
        assert sql == m.closure(m.arcs_for_tier(LINKS, FLOW, SOUND, tier), ["S1"])["affected"]
    assert [n for (n,) in db.execute(CLOSURE_SQL, {"tier": 1})] == ["R1", "S1", "S2", "S3", "T1"]


def test_sql_recursive_cte_equals_the_reference_on_200_seeded_typed_graphs() -> None:
    """SEEDED: the store form of the closure (view plus recursive CTE) equals the reference at every tier on random
    typed graphs with cycles, several roots and a mix of link kinds (the single worked example above is not enough)."""
    kinds = sorted(FLOW)
    names = {0: "must", 1: "may", 2: "heuristic"}
    for seed in range(200):
        rng = random.Random(5000 + seed)
        nodes = [f"n{i:02d}" for i in range(rng.randrange(2, 14))]
        links = sorted({(rng.choice(nodes), rng.choice(kinds), rng.choice(nodes)) for _ in range(rng.randrange(0, 30))})
        roots = sorted({rng.choice(nodes) for _ in range(rng.randrange(1, 4))})
        db = sqlite3.connect(":memory:")
        db.execute("CREATE TABLE edge(src TEXT NOT NULL, type TEXT NOT NULL, dst TEXT NOT NULL, origin TEXT NOT NULL, "
                   "soundness TEXT NOT NULL, method TEXT NOT NULL, digest TEXT NOT NULL, PRIMARY KEY(src, type, dst)) WITHOUT ROWID")
        db.execute(FLOW_TABLE_SQL)
        db.execute("CREATE TABLE root(node TEXT)")
        db.executemany("INSERT INTO edge VALUES (?,?,?,?,?,?,?)",
                       [(s, t, d, "derived", names[SOUND[t]], "none", "") for s, t, d in links])
        db.executemany("INSERT INTO flow VALUES (?,?,?)", [(t, int("F" in FLOW[t]), int("R" in FLOW[t])) for t in kinds])
        db.executemany("INSERT INTO root VALUES (?)", [(r,) for r in roots])
        db.execute(ARC_VIEW_SQL)
        for tier in (0, 1, 2):
            sql = [n for (n,) in db.execute(CLOSURE_SQL, {"tier": tier})]
            assert sql == m.closure(m.arcs_for_tier(links, FLOW, SOUND, tier), roots)["affected"], (seed, tier)
        db.close()


def test_suspect_far_ends_lie_inside_the_impact_set_when_flow_covers_the_anchor() -> None:
    """The lint that ties suspicion to impact: flow must include the direction away from the anchored endpoint."""
    rng = random.Random(9)
    counterexamples = positives = 0
    for _trial in range(600):
        names = [f"n{i}" for i in range(7)]
        types = {f"t{i}": (rng.choice(["F", "R", "FR"]), rng.choice(["src", "dst", None]), rng.randrange(3)) for i in range(4)}
        links = [(rng.choice(names), rng.choice(sorted(types)), rng.choice(names)) for _ in range(rng.randrange(1, 12))]
        flow = {k: v[0] for k, v in types.items()}
        anchor = {k: v[1] for k, v in types.items()}
        soundness = {k: v[2] for k, v in types.items()}
        changed = sorted({rng.choice(names) for _ in range(rng.randrange(1, 3))})
        stale = set(m.suspect_far_ends(links, anchor, set(changed)))
        impact = set(m.tiered_impact(links, flow, soundness, changed)) if links else set(changed)
        if all(m.flow_covers_anchor(flow[k], anchor[k]) and soundness[k] <= 2 for k in types):
            assert stale <= impact
            positives += 1
        elif not stale <= impact:
            counterexamples += 1
    assert positives >= 20
    assert counterexamples > 0  # negative control: dropping the lint really does lose suspect nodes


def test_o11_changeset_overlap_predicts_conflicts_by_tier() -> None:
    a = m.changeset_overlap(LINKS, FLOW, SOUND, ["S1"], ["S4"])
    assert a == {"direct": [], "a_reaches_b": {"S4": 2}, "b_reaches_a": {},
                 "shared": {"R2": 2, "S4": 2, "T2": 2}}
    b = m.changeset_overlap(LINKS, FLOW, SOUND, ["S2"], ["R1"])
    assert b["direct"] == [] and b["a_reaches_b"] == {"R1": 0} and b["b_reaches_a"] == {"S2": 0}
    assert b["shared"] == {"R1": 0, "R2": 2, "S1": 1, "S2": 0, "S3": 1, "S4": 2, "T1": 0, "T2": 2}
    assert m.changeset_overlap(LINKS, FLOW, SOUND, ["S1", "S4"], ["S4"])["direct"] == ["S4"]


def test_changeset_overlap_is_symmetric_and_equals_the_intersection_of_the_two_closures() -> None:
    for seed in range(120):
        rng = random.Random(seed)
        names = [f"n{i}" for i in range(8)]
        types = {f"t{i}": (rng.choice(["F", "R", "FR"]), rng.randrange(3)) for i in range(3)}
        links = [(rng.choice(names), rng.choice(sorted(types)), rng.choice(names)) for _ in range(rng.randrange(1, 14))]
        flow = {k: v[0] for k, v in types.items()}
        snd = {k: v[1] for k, v in types.items()}
        ra, rb = sorted({rng.choice(names)}), sorted({rng.choice(names), rng.choice(names)})
        ab = m.changeset_overlap(links, flow, snd, ra, rb)
        ba = m.changeset_overlap(links, flow, snd, rb, ra)
        assert ab["shared"] == ba["shared"] and ab["direct"] == ba["direct"]
        assert ab["a_reaches_b"] == ba["b_reaches_a"] and ab["b_reaches_a"] == ba["a_reaches_b"]
        ia, ib = m.tiered_impact(links, flow, snd, ra), m.tiered_impact(links, flow, snd, rb)
        assert set(ab["shared"]) == set(ia) & set(ib)
        for n, tier in ab["shared"].items():
            assert tier == max(ia[n]["tier"], ib[n]["tier"])


# ================================================================ O2 SCC, condensation, reach
O2_NODES = list("abcdefgh")
O2_ADJ = {"a": ["b"], "b": ["c", "f"], "c": ["a", "d"], "d": ["e"], "e": ["d"], "g": ["a"]}


def test_o2_condensation_topological_order_and_reach_counts() -> None:
    label, members, dag = m.condensation(O2_NODES, O2_ADJ)
    assert label == {"a": "a", "b": "a", "c": "a", "d": "d", "e": "d", "f": "f", "g": "g", "h": "h"}
    assert members == {"a": ["a", "b", "c"], "d": ["d", "e"], "f": ["f"], "g": ["g"], "h": ["h"]}
    assert dag == {"a": ["d", "f"], "d": [], "f": [], "g": ["a"], "h": []}
    assert m.lex_topological_order(dag) == ["g", "a", "d", "f", "h"]
    assert m.reach_counts(O2_NODES, O2_ADJ) == {"a": 6, "b": 6, "c": 6, "d": 2, "e": 2, "f": 1, "g": 7, "h": 1}
    assert m.exposure_counts(O2_NODES, O2_ADJ) == {"a": 4, "b": 4, "c": 4, "d": 6, "e": 6, "f": 5, "g": 1, "h": 1}


def test_scc_labels_are_permutation_invariant_and_match_mutual_reachability() -> None:
    for seed in range(150):
        names, adj = random_graph(seed)
        label = m.scc_labels(names, adj)
        reach = {n: set(m.closure(adj, [n])["affected"]) for n in names}
        for x, y in itertools.product(names, repeat=2):
            assert (label[x] == label[y]) == (y in reach[x] and x in reach[y])
        assert all(label[n] == min(k for k in names if label[k] == label[n]) for n in names)
        rng = random.Random(seed)
        shuffled = {k: rng.sample(v, len(v)) for k, v in sorted(adj.items(), key=lambda kv: rng.random())}
        assert m.scc_labels(rng.sample(names, len(names)), shuffled) == label
        for n, c in m.reach_counts(names, adj).items():
            assert c == len(reach[n])


def test_lexicographic_topological_order_is_the_minimum_over_all_orders() -> None:
    for seed in range(60):
        rng = random.Random(seed)
        n = rng.randrange(2, 7)
        names = [f"v{i}" for i in range(n)]
        dag = {u: sorted({v for v in names[i + 1:] if rng.random() < 0.4}) for i, u in enumerate(names)}
        perm = list(names)
        rng.shuffle(perm)  # relabel so the DAG order is not the id order
        ren = dict(zip(names, perm, strict=False))
        dag2 = {ren[u]: sorted(ren[v] for v in vs) for u, vs in dag.items()}
        orders = [p for p in itertools.permutations(perm)
                  if all(p.index(u) < p.index(v) for u, vs in dag2.items() for v in vs)]
        assert m.lex_topological_order(dag2) == list(min(orders))


@pytest.mark.skipif(nx is None, reason="networkx not installed (NOT_RUN)")
def test_scc_partition_agrees_with_networkx() -> None:
    for seed in range(100):
        names, adj = random_graph(seed)
        g = nx.DiGraph()
        g.add_nodes_from(names)
        g.add_edges_from((u, v) for u, vs in adj.items() for v in vs)
        theirs = sorted(tuple(sorted(c)) for c in nx.strongly_connected_components(g))
        label = m.scc_labels(names, adj)
        mine = {}
        for n, l in label.items():
            mine.setdefault(l, []).append(n)
        assert sorted(tuple(sorted(v)) for v in mine.values()) == theirs


# ================================================================ O3 personalised PageRank
O3_W = {("A", "B"): 1, ("A", "C"): 1, ("B", "C"): 1, ("C", "A"): 1}


def test_o3_exact_solution_and_integer_result() -> None:
    exact = m.ppr_exact(list("ABC"), O3_W, {"A": 1}, (1, 5))
    assert exact == {"A": F(25, 53), "B": F(10, 53), "C": F(18, 53)}
    r = m.ppr_int(list("ABC"), O3_W, {"A": 1}, (1, 5), bits=24)
    assert r["iterations"] == 78
    assert sum(r["scores"].values()) == r["scale"]  # mass is conserved exactly
    assert r["ppm"] == {"A": 471698, "B": 188679, "C": 339623}
    assert r["ranking"] == ["A", "C", "B"]
    for n in "ABC":
        assert abs(r["scores"][n] - exact[n] * r["scale"]) <= r["err_bound_units"]


def test_o3_dangling_node_returns_to_the_seed() -> None:
    w = {("A", "B"): 1}
    assert m.ppr_exact(list("AB"), w, {"A": 1}, (1, 5)) == {"A": F(5, 9), "B": F(4, 9)}
    r = m.ppr_int(list("AB"), w, {"A": 1}, (1, 5))
    assert r["ppm"] == {"A": 555556, "B": 444444}


def test_ppr_error_bound_holds_on_random_weighted_graphs_with_dangling_nodes() -> None:
    for seed in range(40):
        rng = random.Random(seed)
        n = rng.randrange(2, 9)
        names = [f"n{i}" for i in range(n)]
        w = {(rng.choice(names), rng.choice(names)): rng.randrange(1, 6) for _ in range(rng.randrange(0, 20))}
        seeds = {rng.choice(names): rng.randrange(1, 4) for _ in range(rng.randrange(1, 3))}
        alpha = rng.choice([(1, 5), (1, 3), (1, 2), (1, 10), (2, 7)])
        r = m.ppr_int(names, w, seeds, alpha, bits=20)
        exact = m.ppr_exact(names, w, seeds, alpha)
        assert sum(r["scores"].values()) == r["scale"]
        assert sum(abs(r["scores"][k] - exact[k] * r["scale"]) for k in exact) <= r["err_bound_units"]


def test_ppr_is_bit_identical_under_input_reordering_and_hash_seed() -> None:
    rng = random.Random(3)
    names = [f"n{i:02d}" for i in range(30)]
    w = {(rng.choice(names), rng.choice(names)): rng.randrange(1, 9) for _ in range(120)}
    base = m.ppr_int(names, w, {"n00": 1, "n05": 2}, (1, 5), bits=20)["scores"]
    for s in range(5):
        r2 = random.Random(s)
        items = list(w.items())
        r2.shuffle(items)
        assert m.ppr_int(r2.sample(names, len(names)), dict(items), {"n05": 2, "n00": 1}, (1, 5), bits=20)["scores"] == base
    code = ("import sys,json,importlib.util;"
            "s=importlib.util.spec_from_file_location('r',sys.argv[1]);r=importlib.util.module_from_spec(s);"
            "sys.modules['r']=r;s.loader.exec_module(r);"
            "w={('A','B'):1,('A','C'):1,('B','C'):1,('C','A'):1};"
            "print(json.dumps(r.ppr_int(list('ABC'),w,{'A':1})['scores'],sort_keys=True));"
            "print(json.dumps(r.tiered_impact([('a','x','b'),('b','x','c')],{'x':'F'},{'x':0},['a']),sort_keys=True))")
    outs = set()
    for seed in ("0", "1", "2", "random"):
        env = dict(os.environ, PYTHONHASHSEED=seed)
        outs.add(subprocess.run([sys.executable, "-c", code, str(ROOT / "graph/bench/impact_math_reference.py")],
                                capture_output=True, check=True, env=env).stdout)
    assert len(outs) == 1


def test_choose_iterations_is_exact_integer_arithmetic() -> None:
    assert m.choose_iterations((1, 5), 24) == 78
    assert m.choose_iterations((1, 5), 20) == 66
    k = m.choose_iterations((1, 3), 20)
    assert 2 * (F(2, 3) ** k) <= F(1, 2**20) < 2 * (F(2, 3) ** (k - 1))


@pytest.mark.skipif(not _HAS_PAGERANK_DEPS, reason="networkx, numpy or scipy not installed (NOT_RUN)")
def test_ppr_matches_networkx_float_pagerank_within_error_bound() -> None:
    rng = random.Random(11)
    names = [f"n{i:02d}" for i in range(25)]
    w = {(rng.choice(names), rng.choice(names)): rng.randrange(1, 5) for _ in range(90)}
    seeds = {"n03": 1}
    g = nx.DiGraph()
    g.add_nodes_from(names)
    for (u, v), x in w.items():
        g.add_edge(u, v, weight=x)
    pers = {n: (1.0 if n == "n03" else 0.0) for n in names}
    pr = nx.pagerank(g, alpha=0.8, personalization=pers, dangling=pers, tol=1e-13, max_iter=10000, weight="weight")
    r = m.ppr_int(names, w, seeds, (1, 5), bits=24)
    assert max(abs(pr[n] - r["scores"][n] / r["scale"]) for n in names) < 1e-6


# ================================================================ O4 context selection
def test_o4_context_selection() -> None:
    got = m.select_context({"seed": 40}, {"a": (90, 30), "b": (60, 10), "c": (50, 25), "d": (10, 5)}, 100)
    assert got == {"status": "OK", "chosen": ["a", "b", "d"], "cost": 85, "value": 160, "omitted": ["c"],
                   "omitted_reasons": {"c": "NOT_SELECTED_BUDGET"}}
    # the density greedy alone would return value 2 here; the best-single-item safeguard returns 100
    got_b = m.select_context({}, {"p": (2, 1), "q": (100, 100)}, 100)
    assert got_b["chosen"] == ["q"]
    assert got_b["omitted"] == ["p"] and got_b["omitted_reasons"] == {"p": "NOT_SELECTED_BUDGET"}
    assert m.select_context({"seed": 40}, {"a": (90, 30)}, 30) == {
        "status": "BUDGET_TOO_SMALL", "needed": 40, "chosen": [], "omitted": [], "omitted_reasons": {}}


def test_o4d_nothing_is_dropped_silently() -> None:
    """Every candidate not chosen is listed with a reason; a page too big for the room is not silently lost."""
    got = m.select_context({"seed": 40}, {"big": (1000, 70), "a": (10, 5), "zero": (0, 5), "free": (7, 0)}, 100)
    assert got["chosen"] == ["a"]
    assert got["omitted"] == ["big", "free", "zero"]  # fitting-but-lost first (none), then excluded by id
    assert got["omitted_reasons"] == {"big": "TOO_LARGE_FOR_ROOM", "free": "NON_POSITIVE_COST",
                                      "zero": "NON_POSITIVE_SCORE"}


def test_context_selection_accounts_for_every_candidate() -> None:
    for seed in range(200):
        rng = random.Random(seed)
        items = {f"i{k}": (rng.randrange(-2, 30), rng.randrange(-1, 14)) for k in range(rng.randrange(0, 9))}
        pinned = {"p": rng.randrange(0, 10)}
        got = m.select_context(pinned, items, rng.randrange(1, 40))
        if got["status"] != "OK":
            continue
        assert sorted(got["chosen"] + got["omitted"]) == sorted(items)  # a partition: nothing vanishes
        assert not set(got["chosen"]) & set(got["omitted"])
        assert sorted(got["omitted_reasons"]) == sorted(got["omitted"])


def test_context_selection_is_at_least_half_of_optimum() -> None:
    for seed in range(200):
        rng = random.Random(seed)
        items = {f"i{k}": (rng.randrange(1, 30), rng.randrange(1, 12)) for k in range(rng.randrange(1, 9))}
        budget = rng.randrange(1, 30)
        got = m.select_context({}, items, budget)
        fit = {k: v for k, v in items.items() if v[1] <= budget}
        best = 0
        for r in range(len(fit) + 1):
            for combo in itertools.combinations(sorted(fit), r):
                if sum(fit[i][1] for i in combo) <= budget:
                    best = max(best, sum(fit[i][0] for i in combo))
        assert got["cost"] <= budget
        assert 2 * got["value"] >= best


# ================================================================ O5 set cover
O5_S1 = frozenset({"a1", "a2"})
O5_S2 = frozenset({"b1", "b2", "b3", "b4"})
O5_S3 = frozenset({f"c{i}" for i in range(1, 9)})
O5_A = frozenset({"a1", "b1", "b2", "c1", "c2", "c3", "c4"})
O5_B = frozenset({"a2", "b3", "b4", "c5", "c6", "c7", "c8"})
O5_SETS = {"S1": (1, O5_S1), "S2": (1, O5_S2), "S3": (1, O5_S3), "A": (1, O5_A), "B": (1, O5_B)}


def test_o5_greedy_is_not_optimal_but_within_the_harmonic_bound() -> None:
    universe = set(O5_S1 | O5_S2 | O5_S3)
    assert len(universe) == 14
    g = m.greedy_cover(universe, O5_SETS)
    assert g == {"chosen": ["S3", "S2", "S1"], "cost": 3, "unreachable": []}
    assert m.optimal_cover_cost(universe, O5_SETS) == 2
    assert F(g["cost"], 2) <= m.harmonic(8)  # d = largest set = 8, H(8) = 761/280


def test_o5_weighted_rule_prefers_cost_per_new_element_and_reports_unreachable() -> None:
    sets = {"X": (12, frozenset("123456")), "Y": (3, frozenset("123")), "Z": (3, frozenset("456"))}
    g = m.greedy_cover(set("1234567"), sets)
    assert g == {"chosen": ["Y", "Z"], "cost": 6, "unreachable": ["7"]}
    assert m.optimal_cover_cost(set("123456"), sets) == 6


def test_greedy_cover_ratio_never_exceeds_harmonic_of_max_set_size() -> None:
    for seed in range(300):
        rng = random.Random(seed)
        elems = [f"e{i}" for i in range(rng.randrange(2, 9))]
        sets = {f"s{i}": (rng.randrange(1, 9), frozenset(rng.sample(elems, rng.randrange(1, len(elems) + 1))))
                for i in range(rng.randrange(1, 8))}
        g = m.greedy_cover(set(elems), sets)
        opt = m.optimal_cover_cost(set(elems), sets)
        d = max(len(e) for _, e in sets.values())
        assert opt is not None and g["cost"] >= opt
        assert g["cost"] <= opt * m.harmonic(d)
        keys = list(sets.items())
        random.Random(seed).shuffle(keys)
        assert m.greedy_cover(set(elems), dict(keys)) == g  # insertion order does not matter


# ================================================================ O6 evidence redundancy
def _brute_min_cut(adj: m.Adj, s: str, t: str) -> tuple[int, list[list[str]]]:
    inner = sorted((set(adj) | {v for vs in adj.values() for v in vs}) - {s, t})
    for r in range(len(inner) + 1):
        cuts = [list(c) for c in itertools.combinations(inner, r)
                if t not in m.closure({k: [x for x in v if x not in c] for k, v in adj.items() if k not in c}, [s])["affected"]]
        if cuts:
            return r, cuts
    raise AssertionError


def test_o6_examples() -> None:
    assert m.vertex_connectivity({"R": ["x", "y"], "x": ["z"], "y": ["z"], "z": ["E"]}, "R", "E") == {"k": 1, "cut": ["z"]}
    assert m.vertex_connectivity({"R": ["x", "y"], "x": ["E"], "y": ["E"]}, "R", "E") == {"k": 2, "cut": ["x", "y"]}
    # a chain has two minimum cuts, {u} and {v}; the canonical one is the source-side minimal {u}
    assert m.vertex_connectivity({"R": ["u"], "u": ["v"], "v": ["E"]}, "R", "E") == {"k": 1, "cut": ["u"]}
    assert m.vertex_connectivity({"R": ["a", "b", "c"], "a": ["E"], "b": ["E"], "c": ["E"]}, "R", "E", cap=2)["k"] == 2


def test_vertex_connectivity_equals_brute_force_min_cut_and_canonical_cut_is_source_side_minimal() -> None:
    checked = 0
    for seed in range(200):
        names, adj = random_graph(seed, n_max=8, e_max=18)
        s, t = names[0], names[-1]
        if s == t or t in adj.get(s, []) or t not in m.closure(adj, [s])["affected"]:
            continue
        got = m.vertex_connectivity(adj, s, t)
        k, cuts = _brute_min_cut(adj, s, t)
        assert got["k"] == k and got["cut"] in cuts
        side = lambda c: set(m.closure({a: [x for x in v if x not in c] for a, v in adj.items() if a not in c}, [s])["affected"])  # noqa: E731
        assert all(side(got["cut"]) <= side(c) for c in cuts)
        checked += 1
    assert checked >= 20


# ================================================================ O7 status algebra
def test_o7_join_table_and_laws_exhaustively() -> None:
    table = {x: [m.join_a(x, y) for y in m.EVIDENCE] for x in m.EVIDENCE}
    assert table == {
        "UNKNOWN": ["UNKNOWN", "STALE", "PASS", "FAIL", "CONFLICT"],
        "STALE": ["STALE", "STALE", "PASS", "FAIL", "CONFLICT"],
        "PASS": ["PASS", "PASS", "PASS", "CONFLICT", "CONFLICT"],
        "FAIL": ["FAIL", "FAIL", "CONFLICT", "FAIL", "CONFLICT"],
        "CONFLICT": ["CONFLICT"] * 5,
    }
    for x, y, z in itertools.product(m.EVIDENCE, repeat=3):
        assert m.join_a(x, y) == m.join_a(y, x)
        assert m.join_a(m.join_a(x, y), z) == m.join_a(x, m.join_a(y, z))
    for x in m.EVIDENCE:
        assert m.join_a(x, x) == x and m.join_a(x, "UNKNOWN") == x and m.join_a(x, "CONFLICT") == "CONFLICT"
    for x, y in itertools.product(m.EVIDENCE, repeat=2):  # monotone in the information order
        assert (x, m.join_a(x, y)) in m.INFO_LEQ


def _kernel_aggregate(statuses) -> str:
    with mock.patch.object(kernel_evidence, "assess_receipt", lambda r, s, c, k, *context: r["st"]):
        return kernel_evidence.aggregate_status([{"st": x} for x in statuses], {}, lambda r: True)


def test_o7_join_equals_kernel_on_flat_inputs_and_composes_where_the_kernel_does_not() -> None:
    inputs = ["PASS", "FAIL", "STALE", "UNKNOWN"]
    for n in range(1, 7):
        for p in itertools.product(inputs, repeat=n):
            assert m.fold_a(list(p)) == _kernel_aggregate(p)
            for k in range(1, n):
                assert m.join_a(m.fold_a(list(p[:k])), m.fold_a(list(p[k:]))) == m.fold_a(list(p))
    assert _kernel_aggregate(["PASS", "FAIL", "FAIL"]) == "CONFLICT"
    assert _kernel_aggregate([_kernel_aggregate(["PASS", "FAIL"]), "FAIL"]) == "FAIL"  # kernel roll-up loses CONFLICT
    assert m.join_a(m.fold_a(["PASS", "FAIL"]), "FAIL") == "CONFLICT"


def test_o7_chain_meet_laws_and_the_pass_iff_all_pass_property_for_every_admissible_chain() -> None:
    non_pass = ["FAIL", "CONFLICT", "STALE", "NOT_RUN", "UNKNOWN"]
    values = [*non_pass, "PASS"]
    for perm in itertools.permutations(non_pass):
        chain = (*perm, "PASS")  # any total order with PASS on top
        for x, y, z in itertools.product(values, repeat=3):
            assert m.meet_b(x, y, chain) == m.meet_b(y, x, chain)
            assert m.meet_b(m.meet_b(x, y, chain), z, chain) == m.meet_b(x, m.meet_b(y, z, chain), chain)
        for n in range(1, 4):
            for p in itertools.product(values, repeat=n):
                assert (m.fold_b(list(p), chain) == "PASS") == all(s == "PASS" for s in p)
    assert m.fold_b(["PASS", "NOT_RUN"]) == "NOT_RUN"  # NOT_RUN absorbs PASS
    assert m.fold_b(["FAIL", "NOT_RUN"]) == "FAIL" and m.fold_b(["UNKNOWN", "STALE"]) == "STALE"
    assert m.fold_b(["PASS", "STALE", "PASS"]) == "STALE"


def test_o7_empty_claim_is_not_run_never_vacuously_green() -> None:
    assert m.fold_b([]) == "NOT_RUN"  # the empty meet would be PASS (top): a gate that requires nothing proves nothing
    assert m.fold_a([]) == "UNKNOWN" == _kernel_aggregate([])  # exactly the kernel on the empty receipt list
    with pytest.raises(ValueError):
        m.fold_a(["NOT_RUN"])  # NOT_RUN is a check-level outcome, not a receipt status


def test_o7_link_status_lift_covers_every_status_but_unwanted() -> None:
    assert m.LINK_TO_STATUS == {"COVERED": "PASS", "SUSPECT": "STALE", "ORPHANED": "FAIL", "AMBIGUOUS": "CONFLICT",
                                "UNRESOLVED": "NOT_RUN"}
    assert set(m.LINK_TO_STATUS.values()) <= set(m.CHAIN)


# ================================================================ O8 counting statistics
def test_o8_pass_hat_k_table_and_unbiasedness() -> None:
    assert [m.pass_hat_k(5, 3, k) for k in (1, 2, 3)] == [F(3, 5), F(3, 10), F(1, 10)]
    assert m.pass_hat_k(5, 3, 4) == 0 and m.pass_hat_k(5, 5, 5) == 1
    # E[C(c,k)/C(n,k)] = p^k for c ~ Binomial(n, p): exact for n = 3, p = 1/2, k = 2 (hand value 1/4) and more
    for n in range(2, 7):
        for p in (F(1, 2), F(1, 3), F(9, 10)):
            for k in range(1, n + 1):
                expect = sum(F(m_comb(n, c)) * p**c * (1 - p) ** (n - c) * m.pass_hat_k(n, c, k) for c in range(n + 1))
                assert expect == p**k
    assert sum(F(m_comb(3, c)) * F(1, 8) * m.pass_hat_k(3, c, 2) for c in range(4)) == F(1, 4)


def m_comb(n: int, c: int) -> int:
    from math import comb
    return comb(n, c)


def test_o8_rule_of_three_generator_miss_probability_and_frechet() -> None:
    # exact one-sided 95% bound after n failure-free iid trials: p* = 1 - 0.05^(1/n)
    assert abs((1 - 0.05 ** (1 / 5)) - 0.4507197) < 1e-6 and abs((1 - 0.05 ** (1 / 100)) - 0.0295130) < 1e-6
    assert (1 - F(3, 100)) ** 100 < F(1, 20) < (1 - F(295, 10000)) ** 100  # 3/n is slightly conservative at n = 100
    # n draws miss a failure region of generator mass 1/1000 with probability (999/1000)^1000 = 0.3677 ...
    assert abs(float(m.miss_probability(F(1, 1000), 1000)) - 0.3676954) < 1e-6
    assert m.miss_probability(F(0), 10**6) == 1  # ... and a blind spot (mass 0) is missed with certainty
    assert m.frechet_lower([F(99, 100)] * 20) == F(4, 5) and abs(float(F(99, 100) ** 20) - 0.8179069) < 1e-6
    assert m.frechet_lower([F(99, 100)] * 200) == 0 and abs(float(F(99, 100) ** 200) - 0.1339797) < 1e-6


def test_o8_same_data_three_priors_three_answers() -> None:
    got = [m.beta_posterior_mean(5, 0, a, a) for a in (F(1), F(1, 2), F(0))]
    assert got == [F(6, 7), F(11, 12), F(1)]  # uniform (Laplace), Jeffreys, Haldane
    # subjective-logic projection with W = 2 and base rate 1/2 is the uniform-prior value: b + a*u = 5/7 + 1/7
    r, s, w, a = 5, 0, 2, F(1, 2)
    assert F(r, r + s + w) + a * F(w, r + s + w) == F(6, 7)


# ================================================================ O9 risk vector
def test_o9_risk_vector_dominance_and_lexicographic_order() -> None:
    x = dict(zip(m.RISK_FIELDS, (0, 0, 2, 3, 1, 4, 3, 1), strict=False))
    y = dict(zip(m.RISK_FIELDS, (0, 0, 0, 5, 1, 10, 20, 1), strict=False))
    z = dict(zip(m.RISK_FIELDS, (0, 0, 2, 2, 1, 4, 3, 1), strict=False))
    assert not m.dominates(x, y) and not m.dominates(y, x)  # incomparable: a partial order, no fake total
    assert m.dominates(x, z) and not m.dominates(z, x)
    assert sorted([("Y", y), ("Z", z), ("X", x)], key=lambda t: m.risk_key(t[1]), reverse=True)[0][0] == "X"
    assert [t[0] for t in sorted([("Y", y), ("Z", z), ("X", x)], key=lambda t: m.risk_key(t[1]), reverse=True)] == ["X", "Z", "Y"]


def test_risk_key_is_a_linear_extension_of_dominance() -> None:
    rng = random.Random(5)
    for _ in range(2000):
        a = {f: rng.randrange(0, 4) for f in m.RISK_FIELDS}
        b = {f: rng.randrange(0, 4) for f in m.RISK_FIELDS}
        if m.dominates(a, b):
            assert m.risk_key(a) > m.risk_key(b)


def test_reference_outputs_are_json_serialisable_and_stable() -> None:
    a = json.dumps(m.tiered_impact(LINKS, FLOW, SOUND, ["S1"]), sort_keys=True)
    b = json.dumps(m.tiered_impact(list(reversed(LINKS)), FLOW, SOUND, ["S1"]), sort_keys=True)
    assert a == b


# ================================================================ integration with the formal aspect (eijaref)
FORMAL = ROOT / "graph" / "formal" / "eijaref"


def _load_formal(name: str):
    path = FORMAL / f"{name}.py"
    if not path.exists():
        pytest.skip(f"graph/formal/eijaref/{name}.py absent (NOT_RUN)")
    spec = importlib.util.spec_from_file_location(f"eijaref_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_closure_result_is_a_certificate_the_formal_checker_accepts() -> None:
    """My distance/parent maps are the (rank, parent) certificate of eijaref.closure; its checker does not
    run BFS, so acceptance is an independent confirmation of the positive part, and check_unreachable of the negative."""
    formal = _load_formal("closure")
    for seed in range(200):
        names, adj = random_graph(seed)
        roots = [names[0], names[-1]]
        rep = m.closure(adj, roots)
        edges = {(u, v) for u, vs in adj.items() for v in vs}
        cert = {"C": frozenset(rep["affected"]), "rank": rep["distance"],
                "parent": {k: v for k, v in rep["parent"].items() if v is not None}}
        assert formal.check_certificate(edges, roots, cert) == (True, "accepted")
        assert frozenset(rep["affected"]) == formal.lfp_kleene(adj, roots) == formal.warshall_closure(adj, roots)
        for other in names:
            if other not in rep["affected"]:
                assert formal.check_unreachable(edges, roots, rep["affected"], other) == (True, "accepted")
        if len(rep["affected"]) > len(roots):  # negative control: a forged parent is rejected
            victim = next(n for n in rep["affected"] if rep["parent"][n] is not None)
            bad = dict(cert, parent=dict(cert["parent"], **{victim: victim}))
            assert formal.check_certificate(edges, roots, bad)[0] is False


def test_scc_labels_and_topological_order_agree_with_the_formal_reference_and_pass_its_checkers() -> None:
    formal = _load_formal("order")
    for seed in range(150):
        names, adj = random_graph(seed)
        edges = sorted({(u, v) for u, vs in adj.items() for v in vs})
        label = m.scc_labels(names, adj)
        assert label == formal.scc_labels(names, edges)
        assert formal.check_scc_labels(names, edges, label) == (True, "accepted")
        _, _, dag = m.condensation(names, adj)
        dag_edges = sorted({(u, v) for u, vs in dag.items() for v in vs})
        theirs = formal.lexicographic_topological_order(list(dag), dag_edges)
        assert theirs == m.lex_topological_order(dag)
        assert formal.check_lexicographic_topological_order(list(dag), dag_edges, theirs)[0] is True


def test_status_algebra_agrees_with_the_formal_reference_except_for_two_documented_representation_choices() -> None:
    formal = _load_formal("status")
    kernel_values = m.EVIDENCE
    for a, b in itertools.product(kernel_values, repeat=2):
        assert formal.join2(a, b) == m.join_a(a, b)
    assert tuple(formal.DEFAULT_CHAIN) == m.CHAIN
    assert dict(formal.LIFT) == m.LINK_TO_STATUS
    values = list(m.CHAIN)
    for n in range(1, 4):
        for p in itertools.product(values, repeat=n):
            assert formal.meet(p) == m.fold_b(list(p))
    for chain in formal.all_chains():
        for p in itertools.product(values, repeat=2):
            assert (formal.meet(p, chain) == "PASS") == all(x == "PASS" for x in p)
    # Deviation 1: the formal reference places NOT_RUN below UNKNOWN inside the join (J is six-valued).
    assert formal.join2("NOT_RUN", "UNKNOWN") == "UNKNOWN" and formal.join2("NOT_RUN", "PASS") == "PASS"
    # Deviation 2: its empty join is NOT_RUN; the kernel's aggregate_status([]) and this design's fold_a([]) are UNKNOWN.
    assert formal.join([]) == "NOT_RUN" and m.fold_a([]) == "UNKNOWN" == _kernel_aggregate([])
    # Everything that decides a verdict is shared: the empty meet is NOT_RUN in both.
    assert formal.meet([]) == m.fold_b([]) == "NOT_RUN"


def test_flow_derived_from_the_metamodel_covers_every_anchored_end_by_construction() -> None:
    path = ROOT / "graph" / "schema" / "metamodel.json"
    if not path.exists():
        pytest.skip("graph/schema/metamodel.json absent (NOT_RUN)")
    kinds = json.loads(path.read_text(encoding="utf-8"))["link_types"]
    assert len(kinds) >= 20
    for kind, spec in sorted(kinds.items()):
        flow = m.flow_from_metamodel(spec["affects"], spec["anchor_ends"])
        assert spec["soundness"] in ("must", "may", "heuristic"), kind
        for end in spec["anchor_ends"]:
            assert m.flow_covers_anchor(flow, "src" if end == "from" else "dst"), kind
        if spec["affects"] in ("to_source", "both"):
            assert "R" in flow
        if spec["affects"] in ("to_target", "both"):
            assert "F" in flow


def test_relevance_weights_sum_over_links_and_follow_the_flow() -> None:
    rw = {"depends_on": (2, 1), "satisfies": (2, 1), "verifies": (2, 1), "calls": (2, 1)}
    got = m.relevance_weights([("S2", "depends_on", "S1"), ("S2", "satisfies", "R1")], FLOW, rw)
    # depends_on flow R: impact arc S1 -> S2 (2), its reversal S2 -> S1 (1); satisfies flow FR: both directions keep 2
    assert got == {("R1", "S2"): 2, ("S1", "S2"): 2, ("S2", "R1"): 2, ("S2", "S1"): 1}
    # two links between the same pair add up (last-writer-wins would give 2 and 1)
    twice = m.relevance_weights([("S2", "depends_on", "S1"), ("S2", "calls", "S1")], FLOW, rw)
    assert twice == {("S1", "S2"): 4, ("S2", "S1"): 2}
    # mutual links: S1 -> S2 and S2 -> S1 each get fwd from one link and rev from the other
    mutual = m.relevance_weights([("S1", "depends_on", "S2"), ("S2", "depends_on", "S1")], FLOW, rw)
    assert mutual == {("S1", "S2"): 3, ("S2", "S1"): 3}


def test_relevance_hub_damping_uses_distinct_neighbours() -> None:
    rw = {"depends_on": (2, 1), "calls": (2, 1)}
    flow = {"depends_on": "R", "calls": "R"}
    # S1 and S2 are joined by two links but are one neighbour of each other: deg(S2) = 1 (S1 only)
    got = m.relevance_weights([("S2", "depends_on", "S1"), ("S2", "calls", "S1")], flow, rw, damp=True)
    assert got == {("S1", "S2"): 4 * (65536 // 2), ("S2", "S1"): 2 * (65536 // 2)}


def test_metamodel_rank_weight_and_cover_role_are_read_not_hard_coded() -> None:
    path = ROOT / "graph" / "schema" / "metamodel.json"
    if not path.exists():
        pytest.skip("graph/schema/metamodel.json absent (NOT_RUN)")
    kinds = json.loads(path.read_text(encoding="utf-8"))["link_types"]
    for kind, spec in sorted(kinds.items()):
        # every kind declares them (no default), and today they all equal the ADR's default pair
        assert m.rank_weight_from_metamodel(spec) == m.DEFAULT_RANK_WEIGHT, kind
        assert m.cover_role_from_metamodel(spec) in m.COVER_ROLES, kind
    assert {k for k, v in kinds.items() if v["cover_role"] == "verifier"} == {"verifies"}
    assert {k for k, v in kinds.items() if v["cover_role"] == "observer"} == {"covers"}
    for bad in ({"rank_weight": [0, 0]}, {"rank_weight": [2]}, {"rank_weight": [2, -1]}, {"rank_weight": [1.5, 1]}, {}):
        with pytest.raises(ValueError):
            m.rank_weight_from_metamodel(bad)
    with pytest.raises(ValueError):
        m.cover_role_from_metamodel({"cover_role": "checker"})
