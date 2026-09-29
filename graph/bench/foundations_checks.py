"""Reproducible checks behind docs/weave/research/math-and-cs-foundations.md.

Every check reports MEASURED (it ran and the numbers are real), or NOT_RUN with a reason when an
optional prerequisite (networkx, rfc8785) is missing. Nothing here proves a property for all inputs;
each check is an exhaustive enumeration of a small domain or a seeded sample, and says which.

Read-only use of the kernel: imports ``eija_studio.domain`` from ``src/`` and never writes to it.
Output is canonical ASCII JSON (sorted keys, no timestamps), so two runs on one platform are
byte-identical.

    python graph/bench/foundations_checks.py            # all checks
    python graph/bench/foundations_checks.py --timing   # add one wall-clock number (not deterministic)
"""
from __future__ import annotations

import hashlib
import itertools
import json
import random
import sqlite3
import sys
from functools import reduce
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from eija_studio.domain import evidence as kernel_evidence  # noqa: E402
from eija_studio.domain.impact import closure  # noqa: E402
from eija_studio.domain.models import canonical  # noqa: E402

try:
    import networkx as nx
except ImportError:  # optional
    nx = None
try:
    import rfc8785
except ImportError:  # optional
    rfc8785 = None


def not_run(reason: str) -> dict:
    return {"status": "NOT_RUN", "reason": reason}


def jcs_vs_kernel_canonical() -> dict:
    """C1: where does the kernel's canonical() differ from RFC 8785 (JCS)?"""
    if rfc8785 is None:
        return not_run("rfc8785 not installed")
    cases = {
        "float_1.0": {"a": 1.0},
        "float_1e-7": {"a": 1e-7},
        "float_neg_zero": {"a": -0.0},
        "float_1e21": {"a": 1e21},
        "float_0.1+0.2": {"a": 0.1 + 0.2},
        "int_2**60": {"a": 2**60},
        "key_order_astral_vs_bmp": {"\U00010000": 1, "￿": 2},
        "unicode_line_separator": {"a": " "},
    }
    out = {}
    for name, value in sorted(cases.items()):
        ours = canonical(value)
        try:
            theirs = rfc8785.dumps(value).decode("utf-8")
        except Exception as exc:  # JCS refuses integers outside the IEEE-754 safe range
            theirs = f"ERROR:{type(exc).__name__}"
        out[name] = {"kernel": ascii(ours), "jcs": ascii(theirs), "same": ours == theirs}
    return {"status": "MEASURED", "cases": out,
            "differs": sorted(k for k, v in out.items() if not v["same"])}


def _example_edges() -> list[tuple[str, str]]:
    return [("req:A", "test:1"), ("req:A", "test:2"), ("req:B", "test:2"), ("test:1", "ev:x"),
            ("test:2", "ev:x"), ("test:2", "ev:y"), ("c1", "c2"), ("c2", "c3"), ("c3", "c1"), ("req:B", "c1")]


def graph_order_sensitivity(trials: int = 200) -> dict:
    """C2: which common graph APIs give edge-insertion-order-dependent output?"""
    if nx is None:
        return not_run("networkx not installed")
    from graphlib import TopologicalSorter
    edges = _example_edges()
    acyclic = [e for e in edges if not (e[0].startswith("c") or e[1].startswith("c"))]
    seen: dict[str, set] = {k: set() for k in
                            ("nx.condensation labels", "graphlib static_order", "nx.lexicographical_topological_sort",
                             "sorted SCC member tuples")}
    for seed in range(trials):
        rng = random.Random(seed)
        shuffled = edges[:]
        rng.shuffle(shuffled)
        g = nx.DiGraph()
        g.add_edges_from(shuffled)
        cond = nx.condensation(g)
        seen["nx.condensation labels"].add(json.dumps({str(k): sorted(v["members"]) for k, v in cond.nodes(data=True)},
                                                     sort_keys=True))
        sccs = sorted(tuple(sorted(c)) for c in nx.strongly_connected_components(g))
        seen["sorted SCC member tuples"].add(tuple(sccs))
        ac = acyclic[:]
        rng.shuffle(ac)
        ts = TopologicalSorter()
        for a, b in ac:
            ts.add(b, a)
        seen["graphlib static_order"].add(tuple(ts.static_order()))
        dg = nx.DiGraph()
        dg.add_edges_from(ac)
        seen["nx.lexicographical_topological_sort"].add(tuple(nx.lexicographical_topological_sort(dg)))
    return {"status": "MEASURED", "trials": trials, "distinct_outputs": {k: len(v) for k, v in sorted(seen.items())}}


def pagerank_float_determinism(shuffles: int = 40) -> dict:
    """C3: is PageRank bit-identical across edge-insertion orders? Does rounding fix ranking?"""
    if nx is None:
        return not_run("networkx not installed")
    rng0 = random.Random(7)
    nodes = 300
    edges = sorted({e for e in ((f"n{rng0.randrange(nodes):03d}", f"n{rng0.randrange(nodes):03d}") for _ in range(1500))
                    if e[0] != e[1]})
    raw, rounded, top = set(), set(), set()
    for seed in range(shuffles):
        e = edges[:]
        random.Random(seed).shuffle(e)
        g = nx.DiGraph()
        g.add_edges_from(e)
        pr = nx.pagerank(g, tol=1e-12, max_iter=5000)
        raw.add(hashlib.sha256(json.dumps(sorted(pr.items())).encode()).hexdigest())
        rounded.add(hashlib.sha256(json.dumps(sorted((k, round(v, 10)) for k, v in pr.items())).encode()).hexdigest())
        top.add(tuple(k for k, _ in sorted(pr.items(), key=lambda kv: (-round(kv[1], 10), kv[0]))[:20]))
    return {"status": "MEASURED", "graph": {"nodes": nodes, "edges": len(edges)}, "shuffles": shuffles,
            "distinct_raw_float_hashes": len(raw), "distinct_after_round_1e-10": len(rounded),
            "distinct_top20_id_orders": len(top),
            "caveat": "rounding can straddle a boundary for other graphs; this is a sample, not a proof"}


def _aggregate(statuses) -> str:
    with mock.patch.object(kernel_evidence, "assess_receipt", lambda r, s, c, k, *context: r["st"]):
        return kernel_evidence.aggregate_status([{"st": x} for x in statuses], {}, lambda r: True)


def status_lattice() -> dict:
    """C4: is the kernel's aggregate_status compositional? Compare with a bounded join-semilattice."""
    inputs = ["PASS", "FAIL", "STALE", "UNKNOWN"]
    values = ["UNKNOWN", "STALE", "PASS", "FAIL", "CONFLICT"]
    covers = {("UNKNOWN", "STALE"), ("STALE", "PASS"), ("STALE", "FAIL"), ("PASS", "CONFLICT"), ("FAIL", "CONFLICT")}
    le = {(a, a) for a in values} | covers
    changed = True
    while changed:
        changed = False
        for (a, b), (c, d) in itertools.product(list(le), list(le)):
            if b == c and (a, d) not in le:
                le.add((a, d))
                changed = True

    def lub(a: str, b: str) -> str:
        upper = [x for x in values if (a, x) in le and (b, x) in le]
        least = [x for x in upper if all((x, y) in le for y in upper)]
        assert len(least) == 1
        return least[0]

    def kernel_join(a: str, b: str) -> str:
        return _aggregate([a, b])

    seqs = [p for n in range(1, 7) for p in itertools.product(inputs, repeat=n)]
    return {
        "status": "MEASURED",
        "domain": "all sequences over {PASS,FAIL,STALE,UNKNOWN} of length 1..6, and all triples over 5 values",
        "kernel_aggregate_order_independent": all(_aggregate(p) == _aggregate(tuple(reversed(p))) for p in seqs),
        "kernel_conflict_is_absorbing": kernel_join("CONFLICT", "FAIL") == "CONFLICT",
        "kernel_join_idempotent_on_range": all(kernel_join(a, a) == a for a in values),
        "kernel_join_associative_on_range": all(kernel_join(kernel_join(a, b), c) == kernel_join(a, kernel_join(b, c))
                                                for a, b, c in itertools.product(values, repeat=3)),
        "hierarchical_counterexample": {"flat": _aggregate(["PASS", "FAIL", "FAIL"]),
                                        "rolled_up": _aggregate([_aggregate(["PASS", "FAIL"]), "FAIL"])},
        "lub_semilattice_laws": {
            "commutative": all(lub(a, b) == lub(b, a) for a, b in itertools.product(values, repeat=2)),
            "idempotent": all(lub(a, a) == a for a in values),
            "associative": all(lub(lub(a, b), c) == lub(a, lub(b, c)) for a, b, c in itertools.product(values, repeat=3)),
        },
        "lub_fold_equals_kernel_aggregate_on_flat_inputs": all(reduce(lub, p) == _aggregate(p) for p in seqs),
        "lub_rollup_composes": all(reduce(lub, [reduce(lub, p[:k]), reduce(lub, p[k:])]) == reduce(lub, p)
                                   for p in seqs if len(p) > 1 for k in range(1, len(p))),
    }


def closure_vs_recursive_cte(graphs: int = 300, timing: bool = False) -> dict:
    """C5: kernel impact closure vs SQLite WITH RECURSIVE (and networkx descendants when present)."""
    mismatches = 0
    for seed in range(graphs):
        rng = random.Random(seed)
        n = rng.randrange(2, 40)
        edges = {(f"n{rng.randrange(n)}", f"n{rng.randrange(n)}") for _ in range(rng.randrange(0, 80))}
        graph: dict[str, list[str]] = {}
        for a, b in sorted(edges):
            graph.setdefault(a, []).append(b)
        roots = sorted({f"n{rng.randrange(n)}" for _ in range(rng.randrange(1, 4))})
        ours = closure(graph, roots)["affected"]
        db = sqlite3.connect(":memory:")
        db.execute("create table e(a, b)")
        db.executemany("insert into e values (?, ?)", sorted(edges))
        db.execute("create table r(x)")
        db.executemany("insert into r values (?)", [(x,) for x in roots])
        sql = ("with recursive reach(x) as (select x from r union select e.b from e join reach on e.a = reach.x) "
               "select x from reach order by x")
        via_sql = [x for (x,) in db.execute(sql)]
        agree = ours == via_sql
        if nx is not None:
            g = nx.DiGraph()
            g.add_edges_from(sorted(edges))
            g.add_nodes_from(roots)
            agree = agree and ours == sorted(set(roots).union(*[nx.descendants(g, x) for x in roots]))
        mismatches += 0 if agree else 1
        db.close()
    result = {"status": "MEASURED", "graphs": graphs, "mismatches": mismatches,
              "compared_with": ["sqlite3 WITH RECURSIVE (UNION)"] + (["networkx.descendants"] if nx else [])}
    if timing:
        import time
        rng = random.Random(1)
        big: dict[str, list[str]] = {}
        for _ in range(60000):
            big.setdefault(f"n{rng.randrange(20000)}", []).append(f"n{rng.randrange(20000)}")
        t0 = time.perf_counter()
        closure(big, ["n0"])
        result["timing_20k_nodes_60k_edges_seconds"] = round(time.perf_counter() - t0, 3)
    return result


def main(argv: list[str]) -> int:
    report = {
        "schema": "eija.weave.foundations-checks.v1",
        "python": sys.version.split()[0],
        "networkx": getattr(nx, "__version__", None),
        "sqlite": sqlite3.sqlite_version,
        "C1_jcs_vs_kernel_canonical": jcs_vs_kernel_canonical(),
        "C2_graph_order_sensitivity": graph_order_sensitivity(),
        "C3_pagerank_float_determinism": pagerank_float_determinism(),
        "C4_status_lattice": status_lattice(),
        "C5_closure_vs_recursive_cte": closure_vs_recursive_cte(timing="--timing" in argv),
    }
    text = json.dumps(report, sort_keys=True, indent=2, ensure_ascii=True) + "\n"
    sys.stdout.buffer.write(text.encode("ascii"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
