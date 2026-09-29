"""Quality budgets over a metrics document. One definition, used by tests, the nox sessions and the dashboard.

A budget is a numeric limit with an operator. Limits are of three kinds and the README says which:

  * principled  a design rule that should hold at any size (no dependency cycles, domain imports no
                other layer, Stable Dependencies Principle, R^2 of a linear fit at least 0.8);
  * external    a published human-factors threshold (Doherty 400 ms);
  * ratchet     a limit derived from the CURRENT measured value by a stated rule, so a regression is caught.
                A ratchet is a guard rail, not a claim of quality.

Tiers (how a budget can fail a build):

  * structural  a deterministic function of the source tree (import graph, cyclomatic complexity,
                maintainability index, test inventory). Evaluated by the fast/full sessions. Ratchet limits are
                the measured value plus a stated margin, so unrelated changes do not trip them.
  * release     depends on the machine or on other tools' local output (latency, timing fits, the coverage
                run, other lanes' reports). Evaluated only by the release session on a run that collected
                them. In the structural profile those sections are NOT_RUN, so these budgets are NOT_RUN there
                and can never fail (or pass) a fast/full build.

Duplication rules: complexity per function is gated by the quality lane's ratchet
(`quality/gates/complexity_ratchet.py`, xenon), so there is no maximum-CC budget here; the coverage floor is
read from `[tool.coverage.report].fail_under` (the quality lane's), never copied.

A budget whose input section is NOT_RUN evaluates to NOT_RUN, never PASS. Timing budgets are measurements
on the machine that ran them; they use generous headroom and the report says so.
"""
from __future__ import annotations

import operator
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from . import inventory
from .common import DOHERTY_MS, FAIL, NOT_RUN, PASS

OPS: dict[str, Callable[[Any, Any], bool]] = {"<=": operator.le, ">=": operator.ge, "==": operator.eq,
                                             "<": operator.lt, ">": operator.gt}
Extract = Callable[[dict], Any]


@dataclass(frozen=True)
class Budget:
    id: str
    description: str
    section: str
    kind: str  # structural | timing
    tier: str  # structural (fast/full) | release
    basis: str  # principled | external | ratchet
    op: str
    limit: Any
    extract: Extract


class Missing(Exception):
    """Raised by an extractor when its section is NOT_RUN or lacks the value; yields status NOT_RUN."""


def _sec(doc: dict, name: str) -> dict:
    section = doc["sections"].get(name)
    if not section or section.get("status") != "MEASURED":
        raise Missing(f"section {name} is NOT_RUN")
    return section


def _layer(doc: dict, name: str) -> dict:
    return next(r for r in _sec(doc, "martin")["layers"] if r["name"] == name)


def _worst_p95(doc: dict, transport: str, kinds: tuple[str, ...]) -> float:
    t = _sec(doc, "performance")["transports"][transport]
    if t.get("status") != "MEASURED":
        raise Missing(f"transport {transport} is NOT_RUN")
    values = [e["p95_ms"] for e in t["endpoints"] if e["kind"] in kinds]
    if not values:
        raise Missing("no endpoints of this kind measured")
    return max(values)


def _non_domain_distance(doc: dict) -> float:
    values = [r["distance"] for r in _sec(doc, "martin")["layers"] if r["name"] != "domain" and r["distance"] is not None]
    return max(values)


def _ab_share(doc: dict) -> float:
    o = _sec(doc, "complexity")["overall"]
    return (o["ranks"]["A"] + o["ranks"]["B"]) / o["functions"]


def _untested_layers(doc: dict) -> list[str]:
    layers = _sec(doc, "tests")["by_layer"]
    return sorted(r["layer"] for r in layers if r["layer"] in {"domain", "application", "adapters", "interfaces"}
                  and r["tests_direct"] == 0)


def _lane_fail(doc: dict) -> int:
    groups = [g for g in _sec(doc, "lane_reports")["groups"] if g["status"] != NOT_RUN]
    if not groups:
        raise Missing("no other lane has written reports")
    return sum(g["status"] == "FAIL" for g in groups)


def _cov(doc: dict, key: str) -> float:
    return _sec(doc, "coverage")["summary"][key]


def _closure(doc: dict, key: str) -> float:
    return _sec(doc, "scaling")["fit"][key]


# Ratchet method (structural tier): limit = the measured value rounded up (down for a floor) to the next 0.05, then
# 0.05 of headroom (0.05 for a share). Measured on main at 577c016 (2026-09-29): max non-domain D 0.432 -> 0.50,
# mean D 0.318 -> 0.40, A/B share 0.985 -> 0.95. Tighten by a deliberate commit; never loosen without a stated reason.
BUDGETS: tuple[Budget, ...] = (
    Budget("ARCH-01", "No dependency cycle between layers", "martin", "structural", "structural", "principled", "==", 0,
           lambda d: len(_sec(d, "martin")["summary"]["layer_cycles"])),
    Budget("ARCH-02", "No import cycle between modules", "martin", "structural", "structural", "principled", "==", 0,
           lambda d: len(_sec(d, "martin")["summary"]["module_cycles"])),
    Budget("ARCH-03", "No Stable Dependencies Principle violation (a layer never depends on a less stable one)", "martin",
           "structural", "structural", "principled", "==", 0, lambda d: len(_sec(d, "martin")["summary"]["sdp_violations"])),
    Budget("ARCH-04", "Domain layer imports no other layer (Ce = 0)", "martin", "structural", "structural", "principled", "==", 0,
           lambda d: _layer(d, "domain")["ce"]),
    Budget("ARCH-05", "Domain layer is maximally stable (I <= 0.1)", "martin", "structural", "structural", "principled", "<=", 0.1,
           lambda d: _layer(d, "domain")["instability"]),
    Budget("ARCH-06", "Every non-domain layer lies within 0.5 of the main sequence (max D)", "martin",
           "structural", "structural", "ratchet", "<=", 0.5, _non_domain_distance),
    Budget("ARCH-07", "Mean layer distance from the main sequence (the domain layer's D of 1.0 is included)",
           "martin", "structural", "structural", "ratchet", "<=", 0.4, lambda d: _sec(d, "martin")["summary"]["mean_layer_distance"]),
    Budget("CX-02", "Share of functions ranked A or B (CC <= 10)", "complexity", "structural", "structural",
           "ratchet", ">=", 0.95, _ab_share),
    Budget("CX-03", "Lowest module maintainability index (radon MI, rank A >= 20)", "complexity", "structural", "structural",
           "principled", ">=", 20, lambda d: _sec(d, "complexity")["summary"]["min_mi"]),
    Budget("TEST-01", "Every domain/application/adapters/interfaces layer has a directly importing test (count of untested)",
           "tests", "structural", "structural", "principled", "==", 0, lambda d: len(_untested_layers(d))),
    Budget("COV-01", "Line+branch coverage of src/eija_studio, percent, at least the quality lane's floor (pyproject fail_under)",
           "coverage", "structural", "release", "ratchet", ">=", inventory.coverage_floor(), lambda d: _cov(d, "percent")),
    Budget("LANE-01", "No aggregated lane report has status FAIL", "lane_reports", "structural", "release", "principled", "==", 0,
           _lane_fail),
    Budget("PERF-01", "p95 of every read endpoint under 400 ms (TestClient)", "performance", "timing", "release", "external", "<",
           DOHERTY_MS, lambda d: _worst_p95(d, "testclient", ("read",))),
    Budget("PERF-02", "p95 of every non-compute write endpoint under 400 ms (TestClient, durable SQLite)", "performance",
           "timing", "release", "external", "<", DOHERTY_MS, lambda d: _worst_p95(d, "testclient", ("write",))),
    Budget("PERF-03", "p95 of every read and write endpoint under 400 ms (real uvicorn, loopback)", "performance", "timing",
           "release", "external", "<", DOHERTY_MS, lambda d: _worst_p95(d, "uvicorn", ("read", "write"))),
    Budget("PERF-04", "p95 of the verify compute endpoint under 10 s (long-running: needs a progress indication, see README)",
           "performance", "timing", "release", "external", "<", 10_000.0, lambda d: _worst_p95(d, "testclient", ("compute",))),
    Budget("PERF-05", "Runtime verification time is linear in matrix size (R^2 of T = c0 + c1*cells)", "performance", "timing",
           "release", "principled", ">=", 0.8, lambda d: _sec(d, "performance")["verify_scaling"]["r2"]),
    Budget("SCALE-01", "closure(): two-term linear fit T = c0 + cV*V + cE*E, R^2", "scaling", "timing", "release", "principled",
           ">=", 0.8, lambda d: _closure(d, "two_term_r2")),
    Budget("SCALE-02", "closure(): log-log exponent of time against V+E lies in [0.7, 1.3] (quadratic growth would give 2)", "scaling",
           "timing", "release", "principled", "==", True, lambda d: 0.7 <= _closure(d, "loglog_exponent") <= 1.3),
    Budget("SCALE-03", "closure(): linear fit beats the quadratic alternative (R^2 difference)", "scaling", "timing", "release",
           "principled", ">", 0.0, lambda d: round(_closure(d, "r2") - _closure(d, "alt_quadratic_r2"), 6)),
)


def evaluate(doc: dict, budgets: tuple[Budget, ...] = BUDGETS) -> list[dict]:
    results = []
    for b in budgets:
        row = {"id": b.id, "description": b.description, "section": b.section, "kind": b.kind, "tier": b.tier,
               "basis": b.basis, "op": b.op, "limit": b.limit}
        try:
            actual = b.extract(doc)
        except (Missing, KeyError, StopIteration, ValueError, TypeError) as exc:
            results.append({**row, "actual": None, "status": NOT_RUN, "reason": str(exc) or exc.__class__.__name__})
            continue
        results.append({**row, "actual": actual, "status": PASS if OPS[b.op](actual, b.limit) else FAIL})
    return results


def summary(results: list[dict]) -> dict:
    counts = {PASS: 0, FAIL: 0, NOT_RUN: 0}
    for r in results:
        counts[r["status"]] += 1
    return counts
