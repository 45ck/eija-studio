"""Storage-and-query probe for docs/weave/design/storage-and-query.md and graph/bench/PLAN.md.

Two kinds of output, kept apart on purpose (determinism doctrine):

* ``deterministic``: counts, hashes and booleans. Two runs must give byte-identical JSON
  (the script prints ``deterministic_sha256`` so this is checkable).
* ``timing``: wall-clock medians. Never compared byte-for-byte.

Standard library only (``sqlite3``); DuckDB and networkx are optional and their absence is reported
as NOT_RUN, never as a pass. Scratch files live in ``<worktree>/.tmp/storage-probe`` and ``main()`` points TMP and TEMP
there (D-21); importing this module changes nothing in the environment.
Run serially:  python graph/bench/storage_query_probe.py [--sizes 10000 100000 1000000] [--sizing ROOT ...]
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import platform
import random
import shutil
import sqlite3
import statistics
import subprocess
import sys
import time
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[2]
SCRATCH = WORKTREE / ".tmp" / "storage-probe"

DDL = """
CREATE TABLE node(id TEXT PRIMARY KEY, type TEXT NOT NULL, content_hash TEXT NOT NULL) WITHOUT ROWID;
CREATE TABLE edge(src TEXT NOT NULL, type TEXT NOT NULL, dst TEXT NOT NULL, origin TEXT NOT NULL,
                  PRIMARY KEY(src, type, dst)) WITHOUT ROWID;
"""
DDL_REV = "CREATE INDEX edge_rev ON edge(dst, type, src);"
DDL_ROWID = """
CREATE TABLE node(id TEXT PRIMARY KEY, type TEXT NOT NULL, content_hash TEXT NOT NULL);
CREATE TABLE edge(src TEXT NOT NULL, type TEXT NOT NULL, dst TEXT NOT NULL, origin TEXT NOT NULL,
                  PRIMARY KEY(src, type, dst));
"""
CLOSURE_SQL = (
    "WITH RECURSIVE r(x) AS (SELECT id FROM root UNION "
    "SELECT e.dst FROM edge e JOIN r ON e.src = r.x WHERE e.type IN ('depends_on','satisfies')) "
    "SELECT x FROM r ORDER BY x"
)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def jl(row) -> bytes:
    """One canonical line: JSON array of strings, ensure_ascii=False, no spaces (a JCS-subset for arrays)."""
    return (json.dumps(list(row), separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def timed(fn, repeats=3):
    out, ts = None, []
    for _ in range(repeats):
        t = time.perf_counter()
        out = fn()
        ts.append(time.perf_counter() - t)
    return out, statistics.median(ts)


# ---------------------------------------------------------------- synthetic typed graph
def make_graph(n_edges: int, seed: int = 11):
    """Typed EIJA-like graph. Returns (nodes, edges, seeded_untested_requirements, roots)."""
    rng = random.Random(seed)
    n_s, n_r, n_t = n_edges // 5, max(10, n_edges // 20), max(10, n_edges // 10)
    S = [f"repo://src/m{i // 20}.py#s{i}" for i in range(n_s)]
    R = [f"repo://docs/req.csv#R{i}" for i in range(n_r)]
    T = [f"repo://tests/t{i // 20}.py#t{i}" for i in range(n_t)]
    nodes = [(x, "symbol") for x in S] + [(x, "requirement") for x in R] + [(x, "test") for x in T]
    edges: set[tuple[str, str, str]] = set()
    untested = set()
    for r in R:
        for s in rng.sample(S, rng.randint(1, 3)):
            edges.add((s, "satisfies", r))
        if rng.random() < 0.08:
            untested.add(r)
        else:
            for t in rng.sample(T, rng.randint(1, 2)):
                edges.add((t, "verifies", r))
    for t in T:
        for s in rng.sample(S, 3):
            edges.add((t, "covers", s))
    while len(edges) < n_edges:  # symbol-to-symbol depends_on: mostly forward, ~2% back edges (cycles)
        a = rng.randrange(n_s)
        b = rng.randrange(n_s) if rng.random() < 0.02 else min(n_s - 1, a + 1 + int(rng.expovariate(1 / 20)))
        if a != b:
            edges.add((S[a], "depends_on", S[b]))
    node_rows = sorted((i, t, sha(i.encode())[:16]) for i, t in nodes)
    edge_rows = sorted((a, t, b, "derived") for a, t, b in edges)
    return node_rows, edge_rows, sorted(untested), S[:5]


def load(con, nodes, edges, rev_index=True):
    con.executescript(DDL)
    con.executemany("INSERT INTO node VALUES(?,?,?)", nodes)
    con.executemany("INSERT INTO edge VALUES(?,?,?,?)", edges)
    if rev_index:
        con.execute(DDL_REV)
    con.commit()


# ---------------------------------------------------------------- witness (lexicographically smallest shortest path)
def lexmin_shortest(adj: dict[str, list[str]], roots: list[str]) -> dict[str, str | None]:
    """parent map of the lexicographically smallest shortest path from any root, by rank propagation.

    Definition: among all shortest paths (as node-id sequences) from a root to v, the smallest sequence
    under tuple comparison. Because all candidates for v have equal length, comparing them equals
    comparing their prefixes; rank at level d+1 sorts by (rank of parent, id). O(E log V), no path tuples.
    """
    parent: dict[str, str | None] = {}
    rank: dict[str, int] = {}
    frontier = sorted(set(roots))
    for i, r in enumerate(frontier):
        parent[r], rank[r] = None, i
    while frontier:
        cand: dict[str, str] = {}
        for u in frontier:
            for v in adj.get(u, ()):
                if v in rank:
                    continue
                p = cand.get(v)
                if p is None or rank[u] < rank[p]:
                    cand[v] = u
        nxt = sorted(cand, key=lambda v: (rank[cand[v]], v))
        for i, v in enumerate(nxt):
            parent[v], rank[v] = cand[v], i
        frontier = nxt
    return parent


def bfs_first_parent(adj, roots):
    """Naive alternative: FIFO BFS, sorted neighbours, parent = first discoverer."""
    from collections import deque
    parent, q = {}, deque(sorted(set(roots)))
    for r in q:
        parent[r] = None
    while q:
        u = q.popleft()
        for v in sorted(adj.get(u, ())):
            if v not in parent:
                parent[v] = u
                q.append(v)
    return parent


def path_of(parent, v):
    out = []
    while v is not None:
        out.append(v)
        v = parent[v]
    return tuple(reversed(out))


def brute_lexmin(adj, roots):
    """Oracle: enumerate every shortest path, take the tuple minimum."""
    from collections import deque
    dist, q = {}, deque(sorted(set(roots)))
    for r in q:
        dist[r] = 0
    while q:
        u = q.popleft()
        for v in adj.get(u, ()):
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    preds: dict[str, list[str]] = {}
    for u in dist:
        for v in adj.get(u, ()):
            if dist.get(v) == dist[u] + 1:
                preds.setdefault(v, []).append(u)

    def all_paths(v):
        if dist[v] == 0:
            yield (v,)
            return
        for p in preds.get(v, ()):
            for path in all_paths(p):
                yield (*path, v)
    return {v: min(all_paths(v)) for v in dist}


def witness_checks(graphs=600):
    mism_oracle = mism_perm = differs_from_bfs = total_paths = 0
    for seed in range(graphs):
        rng = random.Random(seed)
        n = rng.randint(3, 13)
        names = [f"n{i:02d}" for i in range(n)]
        edges = sorted({(rng.choice(names), rng.choice(names)) for _ in range(rng.randint(n, 3 * n))})
        edges = [e for e in edges if e[0] != e[1]]
        roots = rng.sample(names, rng.randint(1, 2))

        def adj_from(es):
            a: dict[str, list[str]] = {}
            for x, y in es:
                a.setdefault(x, []).append(y)
            return a
        base = lexmin_shortest(adj_from(edges), roots)
        oracle = brute_lexmin(adj_from(edges), roots)
        got = {v: path_of(base, v) for v in base}
        mism_oracle += got != oracle
        shuffled = edges[:]
        rng.shuffle(shuffled)
        mism_perm += lexmin_shortest(adj_from(shuffled), roots) != base
        naive = bfs_first_parent(adj_from(edges), roots)
        differs_from_bfs += any(path_of(naive, v) != got[v] for v in got)
        total_paths += len(got)
    return {"graphs": graphs, "paths_checked": total_paths, "mismatches_vs_bruteforce_oracle": mism_oracle,
            "mismatches_under_shuffled_edge_order": mism_perm,
            "graphs_where_first_parent_bfs_gives_a_different_witness": differs_from_bfs}


# ---------------------------------------------------------------- budgeted closure (kernel semantics) vs SQL
def kernel_closure(graph, roots, budget=None):
    """Verbatim copy of src/eija_studio/domain/impact.py::closure (FIFO, sorted roots and neighbours).

    Budget semantics: visits stop once len(visited) >= budget; frontier = queue minus visited. The truncated set
    therefore depends on FIFO visit order, which a recursive CTE does not define (SQLite: undefined without ORDER BY).
    """
    from collections import deque
    queue, visited = deque(sorted(set(roots))), set()
    while queue:
        if budget is not None and len(visited) >= budget:
            frontier = sorted(set(queue) - visited)
            return {"affected": sorted(visited), "complete": not frontier, "frontier": frontier}
        node = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        queue.extend(n for n in sorted(graph.get(node, [])) if n not in visited)
    return {"affected": sorted(visited), "complete": True, "frontier": []}


def _kernel_import_check(cases):
    """Compare the copy with the real kernel function when the source tree is importable; else NOT_RUN."""
    sys.path.insert(0, str(WORKTREE / "src"))
    try:
        from eija_studio.domain.impact import closure as real
    except Exception as exc:  # missing prerequisite is NOT_RUN, never a pass
        return f"NOT_RUN ({type(exc).__name__})"
    finally:
        sys.path.pop(0)
    return sum(real(g, r, b) != kernel_closure(g, r, b) for g, r, b in cases)


def budgeted_closure_checks(graphs=300):
    """H7 split in two: (a) unbounded SQL recursive CTE equals the kernel closure as a set;
    (b) the budgeted Python closure (complete, frontier, truncated set) is unchanged by edge insertion order.
    Also counts, outside the determinism hash, how often a SQL LIMIT budget differs from the kernel's truncation."""
    sql_set_mismatch = perm_mismatch = budgeted_cases = incomplete_cases = 0
    cases = []
    sql_limit_differs = 0
    for seed in range(graphs):
        rng = random.Random(1000 + seed)
        n = rng.randint(4, 40)
        names = [f"n{i:02d}" for i in range(n)]
        edges = sorted({(rng.choice(names), rng.choice(names)) for _ in range(rng.randint(n, 3 * n))})
        edges = [e for e in edges if e[0] != e[1]]
        roots = rng.sample(names, rng.randint(1, 3))
        budget = rng.randint(0, n)

        def adj_from(es):
            a: dict[str, list[str]] = {}
            for x, y in es:
                a.setdefault(x, []).append(y)
            return a
        g = adj_from(edges)
        full = kernel_closure(g, roots)
        con = sqlite3.connect(":memory:")
        con.execute("CREATE TABLE edge(src TEXT NOT NULL, type TEXT NOT NULL, dst TEXT NOT NULL, "
                    "PRIMARY KEY(src,type,dst)) WITHOUT ROWID")
        con.execute("CREATE TABLE root(id TEXT PRIMARY KEY)")
        con.executemany("INSERT INTO edge VALUES(?,?,?)", [(a, "depends_on", b) for a, b in edges])
        con.executemany("INSERT INTO root VALUES(?)", [(r,) for r in roots])
        sql = [x for (x,) in con.execute(CLOSURE_SQL)]
        sql_set_mismatch += sql != full["affected"]
        shuffled = edges[:]
        rng.shuffle(shuffled)
        gs = adj_from(shuffled)
        perm_mismatch += kernel_closure(gs, roots, budget) != kernel_closure(g, roots, budget)
        budgeted = kernel_closure(g, roots, budget)
        budgeted_cases += 1
        incomplete_cases += not budgeted["complete"]
        cases.append((g, roots, budget))
        lim = sorted(x for (x,) in con.execute(
            "WITH RECURSIVE r(x) AS (SELECT id FROM root UNION SELECT e.dst FROM edge e JOIN r ON e.src=r.x) "
            "SELECT x FROM r LIMIT ?", (budget,)))
        sql_limit_differs += lim != budgeted["affected"]
    return {"graphs": graphs, "budgeted_cases": budgeted_cases, "cases_truncated_by_budget": incomplete_cases,
            "sql_unbounded_closure_set_mismatches_vs_kernel_copy": sql_set_mismatch,
            "kernel_copy_budgeted_result_mismatches_under_shuffled_edge_order": perm_mismatch,
            "kernel_copy_vs_real_kernel_mismatches": _kernel_import_check(cases)}, {
        "sqlite_version": sqlite3.sqlite_version,
        "graphs_where_sql_limit_budget_differs_from_kernel_truncated_set": sql_limit_differs,
        "note": "depends on SQLite's undefined queue order without ORDER BY; outside the determinism hash on purpose"}


# ---------------------------------------------------------------- deterministic probes
def file_bytes_vs_insertion_order():
    SCRATCH.mkdir(parents=True, exist_ok=True)
    nodes, edges, _, _ = make_graph(2000)
    out = {}
    for label, ddl, rev in (("without_rowid+rev_index", DDL, True), ("rowid_tables", DDL_ROWID, False)):
        file_hashes, dump_hashes, vac_hashes = [], [], []
        for k in range(6):
            seed = k if k < 5 else 0  # build 5 repeats the insertion order of build 0
            order = list(range(len(edges)))
            random.Random(seed).shuffle(order)
            p = SCRATCH / f"db_{label}_{k}.sqlite"
            p.unlink(missing_ok=True)
            con = sqlite3.connect(p)
            con.executescript(ddl)
            con.executemany("INSERT INTO node VALUES(?,?,?)", random.Random(seed).sample(nodes, len(nodes)))
            con.executemany("INSERT INTO edge VALUES(?,?,?,?)", [edges[i] for i in order])
            if rev:
                con.execute(DDL_REV)
            con.commit()
            h = hashlib.sha256()
            for r in con.execute("SELECT id,type,content_hash FROM node ORDER BY id"):
                h.update(jl(r))
            for r in con.execute("SELECT src,type,dst,origin FROM edge ORDER BY src,type,dst,origin"):
                h.update(jl(r))
            dump_hashes.append(h.hexdigest())
            v = SCRATCH / f"vac_{label}_{k}.sqlite"
            v.unlink(missing_ok=True)
            con.execute(f"VACUUM INTO '{v.as_posix()}'")
            con.close()
            file_hashes.append(sha(p.read_bytes()))
            vac_hashes.append(sha(v.read_bytes()))
        out[label] = {"distinct_file_sha256_over_6_builds": len(set(file_hashes)),
                      "distinct_vacuum_into_sha256": len(set(vac_hashes)),
                      "distinct_logical_dump_sha256": len(set(dump_hashes)),
                      "same_shuffle_built_twice_file_bytes_equal": file_hashes[0] == file_hashes[5]}
    return out


def row_order_without_order_by():
    nodes, edges, _, roots = make_graph(3000)
    plain = ("WITH RECURSIVE r(x) AS (SELECT id FROM root UNION "
             "SELECT e.dst FROM edge e JOIN r ON e.src = r.x WHERE e.type IN ('depends_on','satisfies')) SELECT x FROM r")
    out = {"shuffled_insertion_orders": 8}
    for label, ddl, rev in (("without_rowid", DDL, True), ("rowid_tables", DDL_ROWID, False)):
        outs_plain, outs_sorted, outs_scan = set(), set(), set()
        for k in range(8):
            e = edges[:]
            random.Random(k).shuffle(e)
            con = sqlite3.connect(":memory:")
            con.executescript(ddl)
            con.executemany("INSERT INTO node VALUES(?,?,?)", nodes)
            con.executemany("INSERT INTO edge VALUES(?,?,?,?)", e)
            if rev:
                con.execute(DDL_REV)
            con.execute("CREATE TEMP TABLE root(id TEXT PRIMARY KEY)")
            con.executemany("INSERT INTO root VALUES(?)", [(r,) for r in roots])
            outs_plain.add(sha(jl([x for (x,) in con.execute(plain)])))
            outs_sorted.add(sha(jl([x for (x,) in con.execute(CLOSURE_SQL)])))
            # a plain filtered scan on an unindexed column, the shape most rule queries take
            outs_scan.add(sha(jl([r[0] + r[1] for r in con.execute("SELECT src, dst FROM edge WHERE origin = 'derived'")])))
            con.close()
        out[label] = {"distinct_orders_recursive_closure_without_order_by": len(outs_plain),
                      "distinct_orders_unindexed_filter_scan_without_order_by": len(outs_scan),
                      "distinct_orders_closure_with_total_order_by": len(outs_sorted)}
    return out


def cte_termination():
    """Cycle a->b->c->a plus tail c->d. UNION dedupes whole rows, so extra columns defeat termination."""
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE e(a TEXT, b TEXT)")
    con.executemany("INSERT INTO e VALUES(?,?)", [("a", "b"), ("b", "c"), ("c", "a"), ("c", "d")])
    lim = 1000
    q = {
        "UNION on node only": f"WITH RECURSIVE r(x) AS (SELECT 'a' UNION SELECT b FROM e JOIN r ON a=x LIMIT {lim}) SELECT count(*) FROM r",
        "UNION carrying a path column": f"WITH RECURSIVE r(x,p) AS (SELECT 'a','a' UNION SELECT b, p||'>'||b FROM e JOIN r ON a=x LIMIT {lim}) SELECT count(*) FROM r",
        "UNION carrying a depth column": f"WITH RECURSIVE r(x,d) AS (SELECT 'a',0 UNION SELECT b, d+1 FROM e JOIN r ON a=x LIMIT {lim}) SELECT count(*) FROM r",
        "UNION ALL, no guard except LIMIT": f"WITH RECURSIVE r(x) AS (SELECT 'a' UNION ALL SELECT b FROM e JOIN r ON a=x LIMIT {lim}) SELECT count(*) FROM r",
    }
    res = {k: con.execute(v).fetchone()[0] for k, v in q.items()}
    return {"limit_guard_rows": lim, "rows_returned": res,
            "terminated_by_itself": {k: v < lim for k, v in res.items()}}


def collation_pitfalls():
    con = sqlite3.connect(":memory:")
    items = ["z", "～", "\U0001F600", "a", "B", "é"]
    py = sorted(items)
    sq = [r[0] for r in con.execute("SELECT column1 FROM (VALUES " + ",".join("(?)" for _ in items) + ") ORDER BY column1", items)]
    u16 = sorted(items, key=lambda s: s.encode("utf-16-be"))
    return {"python_sorted_equals_sqlite_binary_order": py == sq,
            "utf16_code_unit_order_equals_codepoint_order": u16 == py,
            "codepoint_order": py, "utf16_order": u16,
            "sqlite_LIKE_A_a_is_case_insensitive": con.execute("SELECT 'A' LIKE 'a'").fetchone()[0] == 1,
            "sqlite_GLOB_A_a_is_case_sensitive": con.execute("SELECT 'A' GLOB 'a'").fetchone()[0] == 0,
            "sqlite_default_collation_is_binary_utf8_memcmp": True}


def query_correctness(n_edges=20000):
    nodes, edges, untested, _roots = make_graph(n_edges)
    con = sqlite3.connect(":memory:")
    load(con, nodes, edges)
    got = [r[0] for r in con.execute(
        "SELECT n.id FROM node n WHERE n.type='requirement' AND NOT EXISTS "
        "(SELECT 1 FROM edge e WHERE e.dst=n.id AND e.type='verifies') ORDER BY n.id")]
    return {"edges": len(edges), "nodes": len(nodes), "seeded_untested_requirements": len(untested),
            "violation_query_rows_equal_seeded_set": got == untested}


def sizing(roots):
    import ast
    import re
    out = {}
    for root in roots:
        r = Path(root)
        files = subprocess.run(["git", "-C", str(r), "ls-files"], capture_output=True, text=True, check=True).stdout.splitlines()
        ext: dict[str, int] = {}
        py_nodes = imports = md_links = repo_uris = 0
        for f in files:
            e = Path(f).suffix or "(none)"
            ext[e] = ext.get(e, 0) + 1
            p = r / f
            try:
                text = p.read_bytes().decode("utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if f.endswith(".py"):
                try:
                    tree = ast.parse(text)
                except SyntaxError:
                    continue
                for n in ast.walk(tree):
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        py_nodes += 1
                    elif isinstance(n, (ast.Import, ast.ImportFrom)):
                        imports += 1
            elif f.endswith(".md"):
                md_links += len(re.findall(r"\]\((?!https?:|#|mailto:)[^)\s]+\)", text))
            repo_uris += text.count("repo://")
        okf_pages = sum(1 for f in files if f.startswith("okf/") and f.endswith(".md"))
        head = subprocess.run(["git", "-C", str(r), "rev-parse", "--short=12", "HEAD"], capture_output=True, text=True).stdout.strip()
        modified = len(subprocess.run(["git", "-C", str(r), "diff", "--name-only"], capture_output=True, text=True).stdout.split())
        out[Path(root).name] = {"head": head, "tracked_files_modified_vs_head": modified, "tracked_files": len(files), "by_extension": dict(sorted(ext.items())),
                                "python_def_and_class_nodes": py_nodes, "python_import_statements": imports,
                                "markdown_relative_links": md_links, "repo_uri_occurrences": repo_uris,
                                "okf_pages": okf_pages}
    return out


# ---------------------------------------------------------------- timing probes
def build_variants(n_edges):
    nodes, edges, untested, roots = make_graph(n_edges)
    res = {}
    SCRATCH.mkdir(parents=True, exist_ok=True)

    def mem():
        con = sqlite3.connect(":memory:")
        load(con, nodes, edges)
        con.close()

    def file_default():
        p = SCRATCH / "b_default.sqlite"
        p.unlink(missing_ok=True)
        con = sqlite3.connect(p)
        load(con, nodes, edges)
        con.close()

    def file_fast():
        p = SCRATCH / "b_fast.sqlite"
        p.unlink(missing_ok=True)
        con = sqlite3.connect(p)
        con.execute("PRAGMA journal_mode=OFF")
        con.execute("PRAGMA synchronous=OFF")
        load(con, nodes, edges)
        con.close()

    reps = 3 if n_edges <= 100_000 else 2
    for name, fn in (("memory", mem), ("file_default_pragmas", file_default), ("file_journal_off_sync_off", file_fast)):
        _, t = timed(fn, reps)
        res[f"build_s_{name}"] = round(t, 3)
    res["index_file_bytes_journal_off"] = (SCRATCH / "b_fast.sqlite").stat().st_size
    # integer-interned variant: ids replaced by rank in sorted order (deterministic)
    rank = {n[0]: i for i, n in enumerate(nodes)}
    int_edges = sorted((rank[a], t, rank[b]) for a, t, b, _ in edges)

    def interned():
        con = sqlite3.connect(":memory:")
        con.execute("CREATE TABLE edge(src INTEGER, type TEXT, dst INTEGER, PRIMARY KEY(src,type,dst)) WITHOUT ROWID")
        con.executemany("INSERT INTO edge VALUES(?,?,?)", int_edges)
        con.commit()
        con.close()
    _, t = timed(interned, reps)
    res["build_s_memory_int_interned_edges_only"] = round(t, 3)
    return nodes, edges, untested, roots, res


def query_timings(nodes, edges, untested, roots):
    con = sqlite3.connect(":memory:")
    load(con, nodes, edges)
    con.execute("CREATE TEMP TABLE root(id TEXT PRIMARY KEY)")
    con.executemany("INSERT INTO root VALUES(?)", [(r,) for r in roots])
    res = {}
    reach, t = timed(lambda: [x for (x,) in con.execute(CLOSURE_SQL)])
    res["closure_5_roots_cte_text_ids_s"] = round(t, 4)
    res["closure_size"] = len(reach)

    rank = {n[0]: i for i, n in enumerate(nodes)}
    ci = sqlite3.connect(":memory:")
    ci.execute("CREATE TABLE edge(src INTEGER, type TEXT, dst INTEGER, PRIMARY KEY(src,type,dst)) WITHOUT ROWID")
    ci.executemany("INSERT INTO edge VALUES(?,?,?)", sorted((rank[a], t, rank[b]) for a, t, b, _ in edges))
    ci.execute("CREATE TABLE root(id INTEGER PRIMARY KEY)")
    ci.executemany("INSERT INTO root VALUES(?)", [(rank[r],) for r in roots])
    got_i, t = timed(lambda: [x for (x,) in ci.execute(CLOSURE_SQL)])
    res["closure_5_roots_cte_int_interned_ids_s"] = round(t, 4)
    assert len(got_i) == len(reach)

    def closure_witness():
        adj: dict[str, list[str]] = {}
        for a, b in con.execute("SELECT src,dst FROM edge WHERE type IN ('depends_on','satisfies') ORDER BY src,dst"):
            adj.setdefault(a, []).append(b)
        par = lexmin_shortest(adj, roots)
        return par
    par, t = timed(closure_witness)
    res["closure_plus_lexmin_witness_python_s"] = round(t, 4)
    assert sorted(par) == reach, "witness map must cover exactly the SQL closure"
    q1 = ("SELECT n.id FROM node n WHERE n.type='requirement' AND NOT EXISTS "
          "(SELECT 1 FROM edge e WHERE e.dst=n.id AND e.type='verifies') ORDER BY n.id")
    got, t = timed(lambda: [r[0] for r in con.execute(q1)])
    res["violation_untested_requirements_anti_join_s"] = round(t, 4)
    assert got == untested
    q2 = ("WITH RECURSIVE r(x) AS (SELECT id FROM root UNION SELECT e.dst FROM edge e JOIN r ON e.src=r.x "
          "WHERE e.type IN ('depends_on','satisfies')) "
          "SELECT x FROM r JOIN node n ON n.id=x WHERE n.type='requirement' AND NOT EXISTS "
          "(SELECT 1 FROM edge e WHERE e.dst=x AND e.type='verifies') ORDER BY x")
    got2, t = timed(lambda: [r[0] for r in con.execute(q2)])
    res["violation_impacted_untested_stratified_s"] = round(t, 4)
    res["violation_impacted_untested_rows"] = len(got2)
    rng = random.Random(3)
    probes = rng.sample([n[0] for n in nodes], 1000)
    lat = []
    for pnode in probes:
        t0 = time.perf_counter()
        con.execute("SELECT dst,type FROM edge WHERE src=? ORDER BY type,dst", (pnode,)).fetchall()
        con.execute("SELECT src,type FROM edge WHERE dst=? ORDER BY type,src", (pnode,)).fetchall()
        lat.append((time.perf_counter() - t0) * 1000)
    lat.sort()
    res["neighbors_in_out_ms_p50_p99"] = [round(lat[len(lat) // 2], 4), round(lat[int(len(lat) * 0.99)], 4)]

    def merkle():
        h = hashlib.sha256()
        for r in con.execute("SELECT id,type,content_hash FROM node ORDER BY id"):
            h.update(jl(r))
        for r in con.execute("SELECT src,type,dst,origin FROM edge ORDER BY src,type,dst,origin"):
            h.update(jl(r))
        return h.hexdigest()
    (_, t) = timed(merkle, 2)
    res["canonical_dump_and_root_hash_s"] = round(t, 3)
    try:
        import duckdb
        d = duckdb.connect(":memory:")
        d.execute("CREATE TABLE node(id VARCHAR, type VARCHAR, content_hash VARCHAR)")
        d.execute("CREATE TABLE edge(src VARCHAR, type VARCHAR, dst VARCHAR, origin VARCHAR)")
        d.executemany("INSERT INTO node VALUES(?,?,?)", nodes)
        import csv
        pth = SCRATCH / "edges.csv"
        with open(pth, "w", newline="\n", encoding="utf-8") as f:
            csv.writer(f, lineterminator="\n").writerows(edges)
        t0 = time.perf_counter()
        d.execute(f"INSERT INTO edge SELECT * FROM read_csv('{pth.as_posix()}', header=false, columns={{'src':'VARCHAR','type':'VARCHAR','dst':'VARCHAR','origin':'VARCHAR'}})")
        res["duckdb_edge_load_s"] = round(time.perf_counter() - t0, 3)
        got, t = timed(lambda: [r[0] for r in d.execute(
            "SELECT n.id FROM node n WHERE n.type='requirement' AND NOT EXISTS "
            "(SELECT 1 FROM edge e WHERE e.dst=n.id AND e.type='verifies') ORDER BY n.id").fetchall()])
        res["duckdb_violation_anti_join_s"] = round(t, 4)
        assert got == untested
    except ImportError:
        res["duckdb"] = "NOT_RUN (duckdb not installed)"
    return res


def extraction_timing(roots):
    """Wall-clock to read and ast.parse every tracked .py file plus read every tracked .md file (warm OS cache)."""
    import ast
    out = {}
    for root in roots:
        r = Path(root)
        files = subprocess.run(["git", "-C", str(r), "ls-files"], capture_output=True, text=True, check=True).stdout.splitlines()
        py = [f for f in files if f.endswith(".py")]
        md = [f for f in files if f.endswith(".md")]

        def run():
            n = 0
            for f in py:
                try:
                    ast.parse((r / f).read_bytes().decode("utf-8"))
                    n += 1
                except (SyntaxError, UnicodeDecodeError, OSError):
                    pass
            for f in md:
                with contextlib.suppress(UnicodeDecodeError, OSError):
                    (r / f).read_bytes().decode("utf-8")
            return n
        n, t = timed(run, 5)
        out[Path(root).name] = {"python_files_parsed": n, "markdown_files_read": len(md), "median_of_5_s": round(t, 3)}
    return out


def cold_start_ms():
    out = {}
    for mod in ("sqlite3", "duckdb", "networkx"):
        ts = []
        for _ in range(5):
            t = time.perf_counter()
            r = subprocess.run([sys.executable, "-c", f"import {mod}"], capture_output=True)
            ts.append((time.perf_counter() - t) * 1000)
            if r.returncode != 0:
                ts = None
                break
        out[f"python_import_{mod}_ms_median"] = round(statistics.median(ts)) if ts else "NOT_RUN (module missing)"
    t = time.perf_counter()
    subprocess.run([sys.executable, "-c", "pass"], capture_output=True)
    out["python_bare_startup_ms_last"] = round((time.perf_counter() - t) * 1000)
    return out


# ---------------------------------------------------------------- pure-Python baseline and real-DDL width
PROPAGATING = ("depends_on", "satisfies")
DDL_WIDE = """
CREATE TABLE node(id TEXT PRIMARY KEY, type TEXT NOT NULL, content_hash TEXT NOT NULL,
                  method TEXT NOT NULL, label TEXT NOT NULL) WITHOUT ROWID;
CREATE TABLE edge(src TEXT NOT NULL, type TEXT NOT NULL, dst TEXT NOT NULL, origin TEXT NOT NULL,
                  soundness TEXT NOT NULL, method TEXT NOT NULL, digest TEXT NOT NULL,
                  PRIMARY KEY(src, type, dst)) WITHOUT ROWID;
CREATE INDEX edge_rev ON edge(dst, type, src);
"""


def python_baseline(n_edges):
    """Option F head-to-head: the same closure, witness, anti-join and stratified violation with no database.

    Every answer is compared with the SQLite answer for the same graph before its time is recorded."""
    nodes, edges, untested, roots = make_graph(n_edges)
    reps = 3 if n_edges <= 100_000 else 2
    res = {"edges": len(edges), "nodes": len(nodes)}

    def build():
        adj: dict[str, list[str]] = {}
        verified: set[str] = set()
        for a, t, b, _ in edges:
            if t in PROPAGATING:
                adj.setdefault(a, []).append(b)
            elif t == "verifies":
                verified.add(b)
        return adj, verified
    (adj, verified), t = timed(build, reps)
    res["build_python_dicts_s"] = round(t, 3)
    reqs = [n[0] for n in nodes if n[1] == "requirement"]

    clo, t = timed(lambda: kernel_closure(adj, roots), reps)
    res["closure_5_roots_kernel_copy_s"] = round(t, 4)
    res["closure_size"] = len(clo["affected"])

    def closure_witness():
        return lexmin_shortest(adj, roots)
    par, t = timed(closure_witness, reps)
    res["closure_plus_lexmin_witness_s"] = round(t, 4)
    assert sorted(par) == clo["affected"]

    anti, t = timed(lambda: sorted(r for r in reqs if r not in verified), reps)
    res["violation_untested_requirements_anti_join_s"] = round(t, 5)
    assert anti == untested
    reqset = set(reqs)
    strat, t = timed(lambda: sorted(x for x in kernel_closure(adj, roots)["affected"]
                                    if x in reqset and x not in verified), reps)
    res["violation_impacted_untested_stratified_s"] = round(t, 4)
    res["violation_impacted_untested_rows"] = len(strat)

    con = sqlite3.connect(":memory:")  # equality check against the SQL answers (untimed)
    load(con, nodes, edges)
    con.execute("CREATE TEMP TABLE root(id TEXT PRIMARY KEY)")
    con.executemany("INSERT INTO root VALUES(?)", [(r,) for r in roots])
    assert [x for (x,) in con.execute(CLOSURE_SQL)] == clo["affected"], "SQL and Python closure differ"
    got = [r[0] for r in con.execute(
        "WITH RECURSIVE r(x) AS (SELECT id FROM root UNION SELECT e.dst FROM edge e JOIN r ON e.src=r.x "
        "WHERE e.type IN ('depends_on','satisfies')) "
        "SELECT x FROM r JOIN node n ON n.id=x WHERE n.type='requirement' AND NOT EXISTS "
        "(SELECT 1 FROM edge e WHERE e.dst=x AND e.type='verifies') ORDER BY x")]
    assert got == strat, "SQL and Python stratified violation differ"
    res["answers_equal_sqlite"] = True
    return res


def wide_ddl(n_edges):
    """File size, build, closure and canonical-dump time with the DDL widths specified in the design
    (5 node columns, 7 edge columns, 64-hex digests). Digests are fake (sha256 of the row) but full width."""
    nodes, edges, _untested, roots = make_graph(n_edges)
    wn = [(i, t, h, "sha256-bytes-v1", i.rsplit("/", 1)[-1]) for i, t, h in nodes]
    we = [(a, t, b, o, "exact", "sha256-bytes-v1", sha(f"{a}|{t}|{b}".encode())) for a, t, b, o in edges]
    SCRATCH.mkdir(parents=True, exist_ok=True)
    pth = SCRATCH / "wide.sqlite"
    pth.unlink(missing_ok=True)
    res = {"edges": len(edges), "nodes": len(nodes)}
    t0 = time.perf_counter()
    con = sqlite3.connect(pth)
    con.execute("PRAGMA journal_mode=OFF")
    con.execute("PRAGMA synchronous=OFF")
    con.executescript(DDL_WIDE)
    con.executemany("INSERT INTO node VALUES(?,?,?,?,?)", wn)
    con.executemany("INSERT INTO edge VALUES(?,?,?,?,?,?,?)", we)
    con.commit()
    res["build_file_journal_off_s"] = round(time.perf_counter() - t0, 3)
    con.close()
    res["index_file_bytes"] = pth.stat().st_size
    con = sqlite3.connect(pth)

    def dump():
        h = hashlib.sha256()
        for r in con.execute("SELECT id,type,content_hash,method,label FROM node ORDER BY id"):
            h.update(jl(r))
        for r in con.execute("SELECT src,type,dst,origin,soundness,method,digest FROM edge ORDER BY src,type,dst"):
            h.update(jl(r))
        return h.hexdigest()
    _, t = timed(dump, 2)
    res["canonical_dump_and_root_hash_s"] = round(t, 3)
    con.execute("CREATE TEMP TABLE root(id TEXT PRIMARY KEY)")
    con.executemany("INSERT INTO root VALUES(?)", [(r,) for r in roots])
    reach, t = timed(lambda: [x for (x,) in con.execute(CLOSURE_SQL)], 2)
    res["closure_5_roots_cte_text_ids_s"] = round(t, 4)
    res["closure_size"] = len(reach)
    con.close()
    pth.unlink(missing_ok=True)
    return res


def baseline_main(sizes):
    os.environ["TMP"] = os.environ["TEMP"] = str(SCRATCH)
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    SCRATCH.mkdir(parents=True)
    out = {"python_baseline": {}, "wide_ddl": {},
           "environment": {"python": platform.python_version(), "sqlite": sqlite3.sqlite_version,
                           "platform": platform.system() + " " + platform.release(),
                           "note": "wall-clock, one machine, shared 16 GB PC, D: HDD scratch; not deterministic; "
                                   "median of 3 (2 at 10^6)"}}
    for m in sizes:
        out["python_baseline"][str(m)] = python_baseline(m)
        print(json.dumps({"python_baseline": m}), file=sys.stderr, flush=True)
    for m in sizes:
        out["wide_ddl"][str(m)] = wide_ddl(m)
        print(json.dumps({"wide_ddl": m}), file=sys.stderr, flush=True)
    out["script_sha256"] = sha(Path(__file__).read_bytes().replace(b"\r\n", b"\n"))
    shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    print(json.dumps(out, sort_keys=True, indent=1, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", nargs="*", type=int, default=[10_000, 100_000, 1_000_000])
    ap.add_argument("--sizing", nargs="*", default=[])
    ap.add_argument("--skip-timing", action="store_true")
    ap.add_argument("--python-baseline", action="store_true",
                    help="only: pure-Python baseline (option F) and real-DDL-width sizing at --sizes")
    a = ap.parse_args()
    if a.python_baseline:
        return baseline_main(a.sizes)
    os.environ["TMP"] = os.environ["TEMP"] = str(SCRATCH)  # D-21: temp files stay inside the worktree .tmp (set here, not at import)
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    SCRATCH.mkdir(parents=True)
    bc_det, bc_obs = budgeted_closure_checks()
    det = {
        "budgeted_closure_checks": bc_det,
        "file_bytes_vs_insertion_order": file_bytes_vs_insertion_order(),
        "row_order_without_order_by": row_order_without_order_by(),
        "recursive_cte_termination": cte_termination(),
        "collation_pitfalls": collation_pitfalls(),
        "witness_checks": witness_checks(),
        "query_correctness": query_correctness(),
    }
    blob = json.dumps(det, sort_keys=True, indent=1, ensure_ascii=False)
    script = Path(__file__).read_bytes().replace(b"\r\n", b"\n")
    out = {"deterministic": det, "deterministic_sha256": sha(blob.encode("utf-8")), "script_sha256": sha(script)}
    out["observations_outside_hash"] = {"budgeted_closure_sql_limit": bc_obs}
    if a.sizing:  # depends on the state of the counted trees, so it is kept outside the determinism hash
        out["repository_counts"] = sizing(a.sizing)
    if not a.skip_timing:
        timing = {"cold_start": cold_start_ms(), "by_edges": {}}
        if a.sizing:
            timing["extraction_stdlib_ast_parse"] = extraction_timing(a.sizing)
        for m in a.sizes:
            nodes, edges, untested, roots, build = build_variants(m)
            q = query_timings(nodes, edges, untested, roots)
            timing["by_edges"][str(m)] = {"nodes": len(nodes), **build, **q}
            print(json.dumps({m: timing["by_edges"][str(m)]}), file=sys.stderr, flush=True)
        timing["environment"] = {"python": platform.python_version(), "sqlite": sqlite3.sqlite_version,
                                 "platform": platform.system() + " " + platform.release(),
                                 "note": "wall-clock, one machine, shared 16 GB PC, D: HDD scratch; not deterministic"}
        out["timing"] = timing
    shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    print(json.dumps(out, sort_keys=True, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
