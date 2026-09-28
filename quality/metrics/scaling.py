"""Empirical scaling model of `eija_studio.domain.impact.closure`.

Hypothesis (from the algorithm: each node is dequeued once and each edge scanned once, with a
per-node sort of out-neighbours): T(V, E) = c0 + c1 * (V + E), i.e. O(V + E) up to the small
`sorted()` factor. This module MEASURES `closure` on seeded synthetic graphs of varying size and
density, fits that model by ordinary least squares, and reports R^2, per-point residuals and the
empirical exponent k of T ~ n^k (slope of the log-log regression; k close to 1 is consistent with
linear growth). It also fits the refinement T = c0 + cV*V + cE*E, because a visited node and a
scanned edge do not cost the same, and a quadratic alternative for comparison.

Graph family: a random recursive tree over V nodes (guarantees every node is reachable from `n0`)
plus extra random edges up to the target out-degree, deduplicated. A closure from `n0` therefore
visits all V nodes and scans all E edges: the worst case for this algorithm on this graph.

What this does NOT establish: an asymptotic proof, behaviour on other graph shapes (e.g. very deep
chains, dense cliques), the cost of building the graph, or performance on another machine. Times are
wall-clock measurements (minimum of repeats, GC paused) and vary run to run.
"""
from __future__ import annotations

import gc
import math
import random
import time
from typing import Callable

from eija_studio.domain.impact import closure

from .common import measured, ols, ols_multi, r3

SEED = 20260928
PROFILES = {  # profile -> (node counts, out-degrees, repeats per point)
    "smoke": ((250, 1000, 4000), (1, 4), 3),  # unit tests only
    "quick": ((250, 500, 1000, 2000, 4000, 8000), (1, 2, 4), 5),
    "full": ((250, 500, 1000, 2000, 4000, 8000, 16000, 32000), (1, 2, 4, 8), 7),
}


def synthetic_graph(nodes: int, degree: int, seed: int = SEED) -> tuple[dict[str, list[str]], int]:
    """Seeded reachable digraph on `nodes` vertices with about `degree * nodes` distinct edges."""
    rng = random.Random(f"{seed}:{nodes}:{degree}")
    names = [f"n{i}" for i in range(nodes)]
    edges: set[tuple[int, int]] = {(rng.randrange(i), i) for i in range(1, nodes)}  # spanning tree from n0
    target = min(degree * nodes, nodes * (nodes - 1))
    while len(edges) < target:
        a, b = rng.randrange(nodes), rng.randrange(nodes)
        if a != b:
            edges.add((a, b))
    graph: dict[str, list[str]] = {}
    for a, b in sorted(edges):
        graph.setdefault(names[a], []).append(names[b])
    return graph, len(edges)


def time_call(fn: Callable[[], object], repeats: int) -> float:
    """Best-of-N wall-clock seconds of `fn` (the minimum, as `timeit` recommends: other processes only ever add
    time), garbage collector paused around each timed call. Used for cost models, not for latency percentiles."""
    samples = []
    for _ in range(repeats):
        gc.collect()
        gc.disable()
        try:
            start = time.perf_counter()
            fn()
            samples.append(time.perf_counter() - start)
        finally:
            gc.enable()
    return min(samples)


def fit_report(points: list[dict]) -> dict:
    """Least-squares fit of T = c0 + c1*(V+E) plus a quadratic alternative and the log-log exponent."""
    xs = [float(p["size"]) for p in points]
    ys = [p["seconds"] * 1000.0 if "seconds" in p else p["ms"] for p in points]  # milliseconds, unrounded when known
    lin = ols(xs, ys)
    quad = ols([x * x for x in xs], ys)  # T = c0 + c2*(V+E)^2, the competing hypothesis
    loglog = ols([math.log(x) for x in xs], [math.log(y) for y in ys])
    two = ols_multi([[p["V"], p["E"]] for p in points], ys)  # T = c0 + cV*V + cE*E: nodes and edges weighted apart
    for p, pred, res, pred2 in zip(points, lin["predicted"], lin["residuals"], two["predicted"]):
        p["predicted_ms"], p["residual_ms"] = r3(pred), r3(res)
        p["two_term_predicted_ms"] = r3(pred2)
        p["residual_pct"] = r3(100 * res / p["ms"]) if p["ms"] else None
    return {"model": "T_ms = c0 + c1 * (V + E)", "c0_ms": round(lin["c0"], 6), "c1_ms_per_element": round(lin["c1"], 9),
            "r2": round(lin["r2"], 6), "max_abs_residual_ms": r3(max(abs(r) for r in lin["residuals"])),
            "two_term_model": "T_ms = c0 + cV * V + cE * E", "two_term_c0_ms": round(two["beta"][0], 6),
            "two_term_cV_ms_per_node": round(two["beta"][1], 9), "two_term_cE_ms_per_edge": round(two["beta"][2], 9),
            "two_term_r2": round(two["r2"], 6),
            "alt_quadratic_r2": round(quad["r2"], 6), "loglog_exponent": round(loglog["c1"], 4),
            "loglog_r2": round(loglog["r2"], 6), "points": len(points),
            "reading": ("Both models are linear in the graph size, so an exponent near 1 with a high R^2 is consistent "
                        "with O(V+E) on this graph family; it is a measurement, not a proof. The single-coefficient "
                        "V+E model fits less well than the two-term model because a visited node costs several "
                        "times more than a scanned edge (queue and per-node sort overhead).")}


def collect(profile: str = "quick") -> dict:
    sizes, degrees, repeats = PROFILES[profile]
    points = []
    for v in sizes:
        for d in degrees:
            graph, e = synthetic_graph(v, d)
            result = closure(graph, ["n0"])
            if not result["complete"] or len(result["affected"]) != v:
                raise RuntimeError("synthetic graph family must be fully reachable from n0")
            seconds = time_call(lambda: closure(graph, ["n0"]), repeats)
            points.append({"V": v, "E": e, "size": v + e, "degree": d, "seconds": seconds, "ms": r3(seconds * 1000)})
    fit = fit_report(points)
    for p in points:
        del p["seconds"]
    return measured(
        kind="measurement", method="repeated wall-clock timing of domain.impact.closure on seeded synthetic graphs",
        source="algorithm: BFS closure, O(V+E); fit: stdlib statistics.linear_regression",
        not_measured=["asymptotic proof", "other graph shapes", "graph construction cost", "other hardware"],
        seed=SEED, repeats=repeats, points=points, fit=fit)
