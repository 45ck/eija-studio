"""Ad hoc MEASUREMENT: transitive-closure engines on a seeded synthetic graph.

Not a kernel benchmark. Inputs are deterministic (random.Random(seed)); timings are wall-clock and
therefore NOT deterministic. Run serially. Usage: python bench_closure_engines.py 1000 100000 1000000
"""
from __future__ import annotations

import json
import platform
import random
import sqlite3
import statistics
import sys
import time
from collections import deque


def make_edges(n_edges: int, seed: int = 7) -> tuple[int, list[tuple[int, int]]]:
    """Mostly-forward edges (a DAG skeleton) plus ~2% back edges so cycles exist."""
    rng = random.Random(seed)
    n = max(8, n_edges // 4)
    edges = set()
    while len(edges) < n_edges:
        a = rng.randrange(n)
        if rng.random() < 0.02:
            b = rng.randrange(n)
        else:
            b = min(n - 1, a + 1 + int(rng.expovariate(1 / 20)))
        if a != b:
            edges.add((a, b))
    return n, sorted(edges)


def eija_closure(graph, roots):  # same algorithm as eija_studio.domain.impact.closure (budget=None)
    queue, visited = deque(sorted(set(roots))), set()
    while queue:
        node = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        queue.extend(x for x in sorted(graph.get(node, [])) if x not in visited)
    return sorted(visited)


def timed(fn, repeats=3):
    out, times = None, []
    for _ in range(repeats):
        t = time.perf_counter()
        out = fn()
        times.append(time.perf_counter() - t)
    return out, statistics.median(times)


def main(sizes):
    rows = []
    for m in sizes:
        n, edges = make_edges(m)
        roots = [0, 1, 2, 3, 4]
        res = {"edges": m, "nodes": n}
        adj: dict[int, list[int]] = {}
        for a, b in edges:
            adj.setdefault(a, []).append(b)
        ref, t = timed(lambda: eija_closure(adj, roots))
        res["python_bfs_s"] = round(t, 4)
        res["closure_size"] = len(ref)

        con = sqlite3.connect(":memory:")
        con.execute("CREATE TABLE e(a INTEGER, b INTEGER, PRIMARY KEY(a,b)) WITHOUT ROWID")
        t0 = time.perf_counter()
        con.executemany("INSERT INTO e VALUES(?,?)", edges)
        res["sqlite_load_s"] = round(time.perf_counter() - t0, 4)
        sql = ("WITH RECURSIVE r(x) AS (SELECT value FROM json_each(?) UNION "
               "SELECT e.b FROM e JOIN r ON e.a=r.x) SELECT x FROM r ORDER BY x")
        got, t = timed(lambda: [x for (x,) in con.execute(sql, (json.dumps(roots),))])
        res["sqlite_cte_s"] = round(t, 4)
        assert got == ref, "sqlite mismatch"

        import duckdb
        import os
        d = duckdb.connect(":memory:")
        d.execute("CREATE TABLE e(a BIGINT, b BIGINT)")
        csv_path = os.path.join(os.environ.get("TMP", "."), "edges.csv")
        with open(csv_path, "w", newline="\n") as f:
            f.write("a,b\n" + "\n".join(f"{a},{b}" for a, b in edges) + "\n")
        t0 = time.perf_counter()
        d.execute("INSERT INTO e SELECT * FROM read_csv(?, header=true, columns={'a':'BIGINT','b':'BIGINT'})", [csv_path])
        res["duckdb_load_s"] = round(time.perf_counter() - t0, 4)
        os.remove(csv_path)
        dsql = ("WITH RECURSIVE r(x) AS (SELECT unnest([0,1,2,3,4]) UNION "
                "SELECT e.b FROM e JOIN r ON e.a=r.x) SELECT x FROM r ORDER BY x")
        got, t = timed(lambda: [x for (x,) in d.execute(dsql).fetchall()])
        res["duckdb_cte_s"] = round(t, 4)
        assert got == ref, "duckdb mismatch"

        import rustworkx as rx
        g = rx.PyDiGraph()
        g.add_nodes_from(range(n))
        g.add_edges_from_no_data(edges)
        def rxc():
            s = set(roots)
            for r in roots:
                s |= rx.descendants(g, r)
            return sorted(s)
        got, t = timed(rxc)
        res["rustworkx_s"] = round(t, 4)
        assert got == ref, "rustworkx mismatch"

        if m <= 100_000:
            import networkx as nx
            G = nx.DiGraph(edges)
            def nxc():
                s = set(roots)
                for r in roots:
                    s |= nx.descendants(G, r)
                return sorted(s)
            got, t = timed(nxc)
            res["networkx_s"] = round(t, 4)
            assert got == ref, "networkx mismatch"
        rows.append(res)
        print(json.dumps(res), flush=True)
    print(json.dumps({"python": platform.python_version(), "platform": platform.platform()}))


if __name__ == "__main__":
    main([int(x) for x in sys.argv[1:]] or [1000, 100000])
