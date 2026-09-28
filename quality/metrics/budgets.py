"""Quality budgets over a metrics document. One definition, used by tests, the nox session and the dashboard.

A budget is a numeric limit with an operator. Limits are of three kinds and the README says which:

  * principled  a design rule that should hold at any size (no dependency cycles, domain imports no
                other layer, Stable Dependencies Principle, R^2 of a linear fit at least 0.9);
  * external    a published human-factors threshold (Doherty 400 ms);
  * ratchet     the current value plus headroom, so a regression is caught (lowest maintainability
                index, coverage floor). A ratchet is a guard rail, not a claim of quality.

Cyclomatic complexity per function is budgeted by the quality lane's `quality/gates/complexity_ratchet.py`
(stricter: default 10 with a pinned debt list); this lane measures and displays it but does not budget it a
second time. Timing budgets (kind `timing`) are advisory in the `full` gate and enforced in the release
session with one re-measurement, because wall-clock values depend on machine load (ADR-0038).

A budget whose input section is NOT_RUN evaluates to NOT_RUN, never PASS. Timing budgets are
measurements on the machine that ran them and can fail under heavy machine load; the report says so.
"""
from __future__ import annotations

import operator
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .common import FAIL, NOT_RUN, PASS

OPS: dict[str, Callable[[Any, Any], bool]] = {"<=": operator.le, ">=": operator.ge, "==": operator.eq,
                                             "<": operator.lt, ">": operator.gt}
Extract = Callable[[dict], "Any"]


@dataclass(frozen=True)
class Budget:
    id: str
    description: str
    section: str
    kind: str  # structural | timing
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


def _untested_layers(doc: dict) -> list[str]:
    layers = _sec(doc, "tests")["by_layer"]
    return sorted(r["layer"] for r in layers if r["layer"] in {"domain", "application", "adapters", "interfaces"}
                  and r["tests_direct"] == 0)


def _lane_fail(doc: dict) -> int:
    """Lane groups that are FAIL or UNKNOWN (unreadable, or a status other than PASS/FAIL/NOT_RUN).

    A report whose status cannot be read is not evidence of success, so it counts against the budget.
    """
    groups = [g for g in _sec(doc, "lane_reports")["groups"] if g["status"] != NOT_RUN]
    if not groups:
        raise Missing("no other lane has written reports")
    return sum(g["status"] in {"FAIL", "UNKNOWN"} for g in groups)


def _cov(doc: dict, key: str) -> float:
    return _sec(doc, "coverage")["summary"][key]


def _verify(doc: dict, key: str) -> float:
    return _sec(doc, "performance")["verify_scaling"][key]


def _closure(doc: dict, key: str) -> float:
    return _sec(doc, "scaling")["fit"][key]


BUDGETS: tuple[Budget, ...] = (
    Budget("ARCH-01", "No dependency cycle between layers", "martin", "structural", "principled", "==", 0,
           lambda d: len(_sec(d, "martin")["summary"]["layer_cycles"])),
    Budget("ARCH-02", "No import cycle between modules", "martin", "structural", "principled", "==", 0,
           lambda d: len(_sec(d, "martin")["summary"]["module_cycles"])),
    Budget("ARCH-03", "No Stable Dependencies Principle violation (a layer never depends on a less stable one)", "martin",
           "structural", "principled", "==", 0, lambda d: len(_sec(d, "martin")["summary"]["sdp_violations"])),
    Budget("ARCH-04", "Domain layer imports no other layer (Ce = 0)", "martin", "structural", "principled", "==", 0,
           lambda d: _layer(d, "domain")["ce"]),
    Budget("ARCH-05", "Domain layer is maximally stable (I <= 0.1)", "martin", "structural", "principled", "<=", 0.1,
           lambda d: _layer(d, "domain")["instability"]),
    Budget("ARCH-06", "Every non-domain layer lies within 0.5 of the main sequence (max D)", "martin", "structural",
           "ratchet", "<=", 0.5, _non_domain_distance),
    Budget("ARCH-07", "Mean layer distance from the main sequence", "martin", "structural", "ratchet", "<=", 0.5,
           lambda d: _sec(d, "martin")["summary"]["mean_layer_distance"]),
    Budget("MI-01", "Lowest module maintainability index (radon MI, rank A >= 20)", "complexity", "structural",
           "ratchet", ">=", 20, lambda d: _sec(d, "complexity")["summary"]["min_mi"]),
    Budget("TEST-01", "Every domain/application/adapters/interfaces layer has a directly importing test (count of untested)",
           "tests", "structural", "principled", "==", 0, lambda d: len(_untested_layers(d))),
    Budget("COV-01", "Line+branch coverage of src/eija_studio, percent (when reports/coverage exists)", "coverage", "structural",
           "ratchet", ">=", 75.0, lambda d: _cov(d, "percent")),
    Budget("LANE-01", "No aggregated lane report is FAIL, UNKNOWN or UNREADABLE (a present report must say PASS or NOT_RUN)", "lane_reports", "structural", "principled", "==", 0, _lane_fail),
    Budget("PERF-01", "p95 of every read endpoint under 400 ms (TestClient)", "performance", "timing", "external", "<", 400.0,
           lambda d: _worst_p95(d, "testclient", ("read",))),
    Budget("PERF-02", "p95 of every non-compute write endpoint under 400 ms (TestClient, durable SQLite)", "performance",
           "timing", "external", "<", 400.0, lambda d: _worst_p95(d, "testclient", ("write",))),
    Budget("PERF-03", "p95 of every read and write endpoint under 400 ms (real uvicorn, loopback)", "performance", "timing",
           "external", "<", 400.0, lambda d: _worst_p95(d, "uvicorn", ("read", "write"))),
    Budget("PERF-04", "p95 of the verify compute endpoint under 10 s (long-running: needs a progress indication, see README)",
           "performance", "timing", "external", "<", 10_000.0, lambda d: _worst_p95(d, "testclient", ("compute",))),
    Budget("PERF-05", "Runtime verification time is near-linear in matrix size (R^2 of T = c0 + c1*cells >= 0.8; measured 0.896 to 0.99 "
           "run to run under load, so the limit keeps headroom; low power, see PERF-06)",
           "performance", "timing", "ratchet", ">=", 0.8, lambda d: _sec(d, "performance")["verify_scaling"]["r2"]),
    Budget("PERF-06", "Runtime verification: linear fit beats the quadratic alternative in cells (R^2 difference)", "performance",
           "timing", "principled", ">", 0.0,
           lambda d: round(_verify(d, "r2") - _verify(d, "alt_quadratic_r2"), 6)),
    Budget("SCALE-01", "closure(): TWO-term fit T = c0 + cV*V + cE*E, R^2 (not the single V+E model; that is SCALE-04)", "scaling",
           "timing", "principled", ">=", 0.9, lambda d: _closure(d, "two_term_r2")),
    Budget("SCALE-04", "closure(): the requested SINGLE-term fit T = c0 + c1*(V+E), R^2 (fits worse than two-term; limit has headroom)",
           "scaling", "timing", "ratchet", ">=", 0.85, lambda d: _closure(d, "r2")),
    Budget("SCALE-02", "closure(): log-log exponent of time against V+E lies in [0.8, 1.2]", "scaling", "timing", "principled",
           "==", True, lambda d: 0.8 <= _closure(d, "loglog_exponent") <= 1.2),
    Budget("SCALE-03", "closure(): linear fit beats the quadratic alternative (R^2 difference)", "scaling", "timing",
           "principled", ">", 0.0, lambda d: round(_closure(d, "r2") - _closure(d, "alt_quadratic_r2"), 6)),
)


def evaluate(doc: dict, budgets: tuple[Budget, ...] = BUDGETS) -> list[dict]:
    results = []
    for b in budgets:
        row = {"id": b.id, "description": b.description, "section": b.section, "kind": b.kind, "basis": b.basis,
               "op": b.op, "limit": b.limit}
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
