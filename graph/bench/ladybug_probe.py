"""Can an embedded Cypher engine reproduce the SQLite closure inside a memory cap? (export-target check)

MEASUREMENT of one question for docs/weave/design/storage-and-query.md: is a one-way export of the EIJA
edge table into Ladybug (the MIT-licensed successor of the archived Kuzu) loadable on Windows, does a
Cypher variable-length pattern return the same reachable set as the reference closure, and at what memory?

SAFETY (shared 16 GB PC; the coordinator, not this script, reported that an earlier uncapped 10,000-edge Ladybug
run reached 8.4 GB resident and killed it. That is an unrecorded anecdote, not reproducible from this repository and
not evidence; the caps below exist because of it, and no decision rests on the figure):
* every process that opens Ladybug first starts an in-process RSS watchdog (sampled every 10 ms) that
  calls ``os._exit(3)`` above ``--rss-limit-mb`` (default 500, hard maximum 500);
* the buffer pool is capped (default 128 MB, hard maximum 256 MB), one thread, ``max_db_size`` 1 GB;
* graphs above 2,000 edges are refused; query children also have a wall-clock timeout;
* on a platform with no RSS probe the probe refuses to run and reports NOT_RUN. Nothing is ever a pass by omission.

Run with a Python that has ``ladybug`` installed (kept out of every EIJA extra):
    .tmp/lbvenv/Scripts/python graph/bench/ladybug_probe.py --edges 1000 [--timeout 30]
Output: JSON on stdout. Timings are wall-clock. Result files: graph/bench/results/ladybug-capped-probe*.json
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import shutil
import sqlite3
import statistics
import subprocess
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import storage_query_probe as sq

PROP = ("depends_on", "satisfies")
WORK = sq.SCRATCH / "lb"
MAX_EDGES, MAX_RSS_MB, MAX_POOL_MB = 2000, 500, 256
PEAK = {"mb": 0.0}


def rss_mb() -> float:
    """Resident set of this process in MB. Raises on platforms without a probe (never guess)."""
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes

        class PMC(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                        ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                        ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]
        pmc = PMC()
        pmc.cb = ctypes.sizeof(PMC)
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.GetCurrentProcess.restype = wintypes.HANDLE
        ps = ctypes.WinDLL("psapi", use_last_error=True)
        ps.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(PMC), wintypes.DWORD]
        if not ps.GetProcessMemoryInfo(k32.GetCurrentProcess(), ctypes.byref(pmc), pmc.cb):
            raise OSError("GetProcessMemoryInfo failed")
        return pmc.WorkingSetSize / 1e6
    if sys.platform.startswith("linux"):
        with open("/proc/self/statm", encoding="ascii") as f:
            return int(f.read().split()[1]) * os.sysconf("SC_PAGE_SIZE") / 1e6
    raise RuntimeError("no RSS probe on this platform")


def start_watchdog(limit_mb: float) -> None:
    rss_mb()  # fail fast if unsupported

    def run():
        while True:
            m = rss_mb()
            PEAK["mb"] = max(PEAK["mb"], m)
            if m > limit_mb:
                sys.stderr.write(f"WATCHDOG: RSS {m:.0f} MB > {limit_mb} MB, aborting\n")
                sys.stderr.flush()
                os._exit(3)
            time.sleep(0.01)
    threading.Thread(target=run, daemon=True).start()


def open_db(path, pool_mb):
    import ladybug as lb
    return lb.Database(str(path), buffer_pool_size=pool_mb * 1024 * 1024, max_num_threads=1,
                       max_db_size=1 << 30)


def rows(result):
    out = []
    while result.has_next():
        out.append(tuple(result.get_next()))
    return out


def query_text(kind: str, bound: int, roots: list[str]) -> str:
    rl = json.dumps(roots)
    if kind == "varlen_default":  # default recursive-pattern semantics
        return (f"MATCH (a:Node)-[:Prop* 1..{bound}]->(x:Node) WHERE a.id IN {rl} "
                f"RETURN DISTINCT x.id ORDER BY x.id")
    if kind == "shortest":  # one shortest path per (a, x)
        return (f"MATCH (a:Node)-[:Prop* SHORTEST 1..{bound}]->(x:Node) WHERE a.id IN {rl} "
                f"RETURN DISTINCT x.id ORDER BY x.id")
    raise ValueError(kind)


def child_query(a) -> None:
    import ladybug as lb
    db = open_db(WORK / "db", a.pool_mb)
    con = lb.Connection(db)
    q = query_text(a.kind, a.bound, json.loads(a.roots))
    ts, got = [], None
    try:
        for _ in range(3):
            t = time.perf_counter()
            got = rows(con.execute(q))
            ts.append(time.perf_counter() - t)
    except RuntimeError as exc:  # an engine refusal under the cap is data, and so is the RSS it reached
        print(json.dumps({"error": f"{type(exc).__name__}: {str(exc)[:200]}", "peak_rss_mb": round(PEAK["mb"])}))
        return
    print(json.dumps({"ids": sorted({r[0] for r in got}), "median_s": round(statistics.median(ts), 4),
                      "peak_rss_mb": round(PEAK["mb"])}))


def child_shuffle(a) -> None:
    import random

    import ladybug as lb
    orders = set()
    prop_edges = sorted(tuple(r) for r in csv.reader(open(WORK / "prop.csv", encoding="utf-8")))
    for k in range(3):
        d = WORK / f"db_shuf{k}"
        shutil.rmtree(d, ignore_errors=True)
        db = open_db(d, a.pool_mb)
        c = lb.Connection(db)
        c.execute("CREATE NODE TABLE Node(id STRING, type STRING, PRIMARY KEY(id))")
        c.execute("CREATE REL TABLE Prop(FROM Node TO Node)")
        sh = prop_edges[:]
        random.Random(k).shuffle(sh)
        with open(WORK / f"prop_shuf{k}.csv", "w", newline="\n", encoding="utf-8") as f:
            csv.writer(f, lineterminator="\n").writerows(sh)
        c.execute(f"COPY Node FROM '{(WORK / 'nodes.csv').as_posix()}' (header=false)")
        c.execute(f"COPY Prop FROM '{(WORK / f'prop_shuf{k}.csv').as_posix()}' (header=false)")
        got = rows(c.execute("MATCH (a:Node)-[:Prop]->(b:Node) RETURN a.id, b.id"))
        orders.add(sq.sha(b"".join(sq.jl(r) for r in got)))
        del c, db
    print(json.dumps({"distinct_orders": len(orders), "peak_rss_mb": round(PEAK["mb"])}))


def run_child(mode_args: list[str], a) -> dict:
    try:
        r = subprocess.run([sys.executable, str(Path(__file__).resolve()), *mode_args,
                            "--pool-mb", str(a.pool_mb), "--rss-limit-mb", str(a.rss_limit_mb)],
                           capture_output=True, text=True, timeout=a.timeout)
    except subprocess.TimeoutExpired:
        return {"result": f"TIMEOUT after {a.timeout} s (child killed; not a pass)"}
    if r.returncode == 3:
        return {"result": f"ABORTED by RSS watchdog above {a.rss_limit_mb} MB (not a pass)"}
    if r.returncode != 0:
        return {"error": r.stderr.strip().splitlines()[-1][:300] if r.stderr.strip() else f"exit {r.returncode}"}
    return json.loads(r.stdout.strip().splitlines()[-1])


def parent(a) -> None:
    try:
        start_watchdog(a.rss_limit_mb)
    except RuntimeError as exc:
        print(json.dumps({"status": "NOT_RUN", "reason": f"{exc}; refusing to run an embedded engine unguarded"}))
        return
    try:
        import ladybug as lb
    except ImportError:
        print(json.dumps({"status": "NOT_RUN", "reason": "ladybug not installed"}))
        return
    shutil.rmtree(WORK, ignore_errors=True)
    WORK.mkdir(parents=True)
    nodes, edges, _, roots = sq.make_graph(a.edges)
    prop_edges = sorted((s, d) for s, t, d, _ in edges if t in PROP)
    adj: dict[str, list[str]] = {}
    for s, d in prop_edges:
        adj.setdefault(s, []).append(d)
    parents = sq.lexmin_shortest(adj, roots)
    reference = sorted(parents)
    depth = max(len(sq.path_of(parents, v)) - 1 for v in parents)
    con_sql = sqlite3.connect(":memory:")
    sq.load(con_sql, nodes, edges)
    con_sql.execute("CREATE TEMP TABLE root(id TEXT PRIMARY KEY)")
    con_sql.executemany("INSERT INTO root VALUES(?)", [(r,) for r in roots])
    assert [x for (x,) in con_sql.execute(sq.CLOSURE_SQL)] == reference

    with open(WORK / "nodes.csv", "w", newline="\n", encoding="utf-8") as f:
        csv.writer(f, lineterminator="\n").writerows([(i, t) for i, t, _ in nodes])
    with open(WORK / "prop.csv", "w", newline="\n", encoding="utf-8") as f:
        csv.writer(f, lineterminator="\n").writerows(prop_edges)
    res = {"edges": len(edges), "nodes": len(nodes), "propagating_edges": len(prop_edges),
           "roots": len(roots), "reference_closure_size": len(reference), "max_bfs_depth_of_reference": depth,
           "caps": {"buffer_pool_mb": a.pool_mb, "max_num_threads": 1, "max_db_size_bytes": 1 << 30,
                    "rss_limit_mb": a.rss_limit_mb, "per_query_timeout_s": a.timeout},
           "rss_mb_before_open": round(rss_mb())}
    t0 = time.perf_counter()
    db = open_db(WORK / "db", a.pool_mb)
    import ladybug as lb
    con = lb.Connection(db)
    con.execute("CREATE NODE TABLE Node(id STRING, type STRING, PRIMARY KEY(id))")
    con.execute("CREATE REL TABLE Prop(FROM Node TO Node)")
    con.execute(f"COPY Node FROM '{(WORK / 'nodes.csv').as_posix()}' (header=false)")
    con.execute(f"COPY Prop FROM '{(WORK / 'prop.csv').as_posix()}' (header=false)")
    res["ladybug_load_s"] = round(time.perf_counter() - t0, 3)
    res["peak_rss_mb_parent_after_load"] = round(PEAK["mb"])
    res["ladybug_version"] = getattr(lb, "__version__", "unknown")
    del con, db  # release the file before children open it

    roots_json = json.dumps(roots)
    variants = [("varlen_default", 3), ("varlen_default", depth + 1), ("varlen_default", 30),
                ("shortest", depth + 1), ("shortest", 30)]
    for kind, bound in variants:
        print(f"{kind} {bound} ...", file=sys.stderr, flush=True)
        out = run_child(["--child-query", "--kind", kind, "--bound", str(bound), "--roots", roots_json], a)
        entry = {"kind": kind, "upper_bound": bound}
        if "ids" in out:
            got = sorted(set(out["ids"]) | set(roots))  # variable-length results exclude a root reached only trivially
            entry.update({"median_s": out["median_s"], "peak_rss_mb": out["peak_rss_mb"], "rows": len(out["ids"]),
                          "equals_reference_after_adding_roots": got == reference,
                          "missing_vs_reference": len(set(reference) - set(got)),
                          "extra_vs_reference": len(set(got) - set(reference))})
        else:
            entry.update(out)
        res[f"{kind}_bound_{bound}"] = entry
    out = run_child(["--child-shuffle"], a)
    res["plain_edge_scan_without_order_by_over_3_shuffled_loads"] = out
    res["environment"] = {"python": platform.python_version(), "platform": platform.system() + " " + platform.release()}
    shutil.rmtree(WORK, ignore_errors=True)
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    print(json.dumps(res, sort_keys=True, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--edges", type=int, default=1000)
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument("--pool-mb", type=int, default=128)
    ap.add_argument("--rss-limit-mb", type=int, default=MAX_RSS_MB)
    ap.add_argument("--child-query", action="store_true")
    ap.add_argument("--child-shuffle", action="store_true")
    ap.add_argument("--kind")
    ap.add_argument("--bound", type=int)
    ap.add_argument("--roots")
    a = ap.parse_args()
    os.environ["TMP"] = os.environ["TEMP"] = str(sq.SCRATCH)  # D-21
    if a.edges > MAX_EDGES or a.pool_mb > MAX_POOL_MB or a.rss_limit_mb > MAX_RSS_MB:
        sys.exit(f"refused: caps are edges<={MAX_EDGES}, pool<={MAX_POOL_MB} MB, rss limit<={MAX_RSS_MB} MB")
    if a.child_query:
        start_watchdog(a.rss_limit_mb)
        child_query(a)
    elif a.child_shuffle:
        start_watchdog(a.rss_limit_mb)
        child_shuffle(a)
    else:
        parent(a)


if __name__ == "__main__":
    main()
