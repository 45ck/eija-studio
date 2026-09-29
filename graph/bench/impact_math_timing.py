"""MEASUREMENT: wall-clock cost of the reference implementations in impact_math_reference.py.

The numbers depend on the machine, Python build and load; they are labelled as such and are never an
artefact input. Graph shapes are seeded and reported, so two runs measure the same work. This is the
reference (clarity first), so a production implementation should be at least as fast.

    python graph/bench/impact_math_timing.py            # prints one JSON document
"""
from __future__ import annotations

import importlib.util
import json
import platform
import random
import sqlite3
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("impact_math_reference", HERE / "impact_math_reference.py")
ref = importlib.util.module_from_spec(spec)
sys.modules["impact_math_reference"] = ref
spec.loader.exec_module(ref)


def graph(n: int, e: int, seed: int = 1) -> tuple[list[str], dict[str, list[str]]]:
    rng = random.Random(seed)
    names = [f"n{i:06d}" for i in range(n)]
    adj: dict[str, set[str]] = {}
    for _ in range(e):
        adj.setdefault(names[rng.randrange(n)], set()).add(names[rng.randrange(n)])
    return names, {k: sorted(v) for k, v in sorted(adj.items())}


def timed(fn, repeat: int = 3) -> float:
    best = None
    for _ in range(repeat):
        t0 = time.perf_counter()
        fn()
        dt = time.perf_counter() - t0
        best = dt if best is None or dt < best else best
    return round(best * 1000, 1)


def main() -> int:
    out = {"label": "MEASUREMENT", "python": platform.python_version(), "platform": platform.platform(),
           "unit": "milliseconds, best of 3", "rows": []}
    for n, e in ((1_000, 5_000), (10_000, 50_000), (100_000, 500_000)):
        names, adj = graph(n, e)
        weights = {(u, v): 1 for u, vs in adj.items() for v in vs}
        row = {"nodes": n, "arcs": sum(len(v) for v in adj.values())}
        row["closure_one_root_ms"] = timed(lambda: ref.closure(adj, [names[0]]))
        row["scc_labels_ms"] = timed(lambda: ref.scc_labels(names, adj), 1 if n >= 100_000 else 3)
        if n <= 10_000:
            row["reach_counts_all_nodes_ms"] = timed(lambda: ref.reach_counts(names, adj), 1)
        if n <= 10_000:
            row["ppr_int_bits20_k66_ms"] = timed(lambda: ref.ppr_int(names, weights, {names[0]: 1}, (1, 5), bits=20), 1)
        else:
            row["ppr_int_bits20_k66_ms"] = None
        db = sqlite3.connect(":memory:")
        db.execute("create table e(a, b)")
        db.executemany("insert into e values (?, ?)", sorted(weights))
        db.execute("create index ea on e(a)")
        sql = ("with recursive reach(x) as (select ?1 union select e.b from e join reach on e.a = reach.x) "
               "select x from reach order by x")
        row["sqlite_recursive_cte_one_root_ms"] = timed(lambda: db.execute(sql, (names[0],)).fetchall())
        out["rows"].append(row)
    rng = random.Random(2)
    for n_elems, n_sets in ((200, 100), (2_000, 1_000)):
        elems = [f"e{i:05d}" for i in range(n_elems)]
        sets = {f"s{i:04d}": (rng.randrange(1, 20), frozenset(rng.sample(elems, rng.randrange(2, 30))))
                for i in range(n_sets)}
        out.setdefault("set_cover", []).append(
            {"elements": n_elems, "sets": n_sets, "greedy_ms": timed(lambda: ref.greedy_cover(set(elems), sets), 1)})
    sys.stdout.write(json.dumps(out, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
