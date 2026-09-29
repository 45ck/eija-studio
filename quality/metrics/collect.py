"""Orchestrate every collector into one document (schema `eija.metrics.v1`, see docs/metrics/README.md).

Top-level keys of `reports/metrics.json`:

    schema, meta{profile, platform, source{commit,dirty}, tools, timing_note, generated_at?},
    sections{martin, complexity, tests, coverage, lane_reports, performance, scaling, verification_yield},
    budgets[{id, description, actual, op, limit, status, kind, section}]

Every section has `status` MEASURED or NOT_RUN (+ `reason`). Sections `performance`, `scaling` and
`verification_yield` hold timing measurements; the rest are deterministic given the source tree.
"""
from __future__ import annotations

from . import ROOT, aggregate, budgets, complexity, inventory, perf, scaling, structure
from .common import dumps, measured, meta, r3, write_text

REPORT = ROOT / "reports" / "metrics.json"
DETERMINISTIC = ("martin", "complexity", "tests", "coverage", "lane_reports")


def structural_sections(*, pytest_collection: bool = True) -> dict:
    """The deterministic sections only (fast, no timing)."""
    lanes = aggregate.collect()
    return {"martin": structure.collect(), "complexity": complexity.collect(),
            "tests": inventory.collect(run_pytest_collection=pytest_collection),
            "coverage": inventory.collect_coverage(), "lane_reports": lanes}


def yield_section(matrix: dict, impact: dict, lanes: dict) -> dict:
    rows = []
    if matrix:
        rows.append({"technique": "runtime_matrix (this kernel)", "kind": "measured-here", "states_explored": matrix["cells"],
                     "findings": matrix["oracle_mismatches"], "duration_s": round(matrix["seconds"], 4),
                     "states_per_s": r3(matrix["cells"] / matrix["seconds"]), "accepted_cells": matrix["accepted"],
                     "denied_cells": matrix["denied"], "status": "MEASURED",
                     "note": "cells = actor x state x action; findings = oracle/runtime disagreements (same-author oracle)"})
    if impact:
        rows.append({"technique": "impact_closure (this kernel)", "kind": "measured-here", "states_explored": impact["nodes"],
                     "findings": None, "duration_s": round(impact["seconds"], 7),
                     "states_per_s": r3(impact["nodes"] / impact["seconds"]), "status": "MEASURED",
                     "note": "nodes of the projection-dependency graph reached from the changed actions"})
    rows += aggregate.yield_rows(lanes)
    lane_rows = [r for r in rows if r["kind"] == "lane-report"]
    return measured(
        kind="measurement", method="states explored per technique: two measured here, the rest copied from lane reports",
        not_measured=["independence of techniques", "defect-finding power (findings are counts reported by each technique)"],
        techniques=rows, summary={"techniques": len(rows), "from_lane_reports": len(lane_rows),
                                  "lane_reports_without_state_counts": max(0, sum(
                                      len(g["reports"]) for g in lanes.get("groups", [])) - len(lane_rows))})


def _measure_timing(sections: dict, profile: str, real_server: bool) -> None:
    """(Re)measure the wall-clock sections in place; the deterministic sections are left untouched."""
    performance, yields = perf.collect(profile, real_server=real_server)
    sections["performance"] = performance
    sections["scaling"] = scaling.collect(profile)
    sections["verification_yield"] = yield_section(yields["matrix"], yields["impact"], sections["lane_reports"])


def _failed_timing(doc: dict) -> list[str]:
    return sorted(r["id"] for r in doc["budgets"] if r["kind"] == "timing" and r["status"] == "FAIL")


def collect(profile: str = "quick", *, generated_at: str | None = None, real_server: bool = True,
            pytest_collection: bool = True, timing_retries: int = 0) -> dict:
    """Measure everything. With `timing_retries` > 0, failed timing budgets trigger a re-measurement of the
    timing sections only; the LAST measurement is reported and `meta.timing_runs` records every run, so a
    pass on a later attempt is never presented as a first-time pass."""
    if profile not in perf.PROFILES:
        raise ValueError(f"unknown profile {profile!r}")
    sections = structural_sections(pytest_collection=pytest_collection)
    _measure_timing(sections, profile, real_server)
    doc = {"schema": meta(profile, generated_at)["schema"], "meta": meta(profile, generated_at), "sections": sections}
    doc["budgets"] = budgets.evaluate(doc)
    runs = [{"run": 1, "failed_timing_budgets": _failed_timing(doc)}]
    for attempt in range(timing_retries):
        if not runs[-1]["failed_timing_budgets"]:
            break
        _measure_timing(sections, profile, real_server)
        doc["budgets"] = budgets.evaluate(doc)
        runs.append({"run": attempt + 2, "failed_timing_budgets": _failed_timing(doc)})
    doc["meta"]["timing_runs"] = runs
    doc["meta"]["timing_policy"] = (f"timing sections measured once, re-measured up to {timing_retries} time(s) when a "
                                    "timing budget failed; the last measurement is reported, earlier failures are listed "
                                    "in timing_runs")
    return doc


def stale_sections(doc: dict) -> list[str]:
    """Deterministic sections of `doc` that no longer match the source tree on disk (martin, complexity only).

    Establishes that the committed snapshot describes the current code structure. It does not check the tests
    or coverage sections (those change with every test added by any lane).
    """
    fresh = structural_sections(pytest_collection=False)
    return sorted(k for k in ("martin", "complexity") if fresh[k] != doc["sections"].get(k))


def write(doc: dict, path=REPORT) -> None:
    write_text(path, dumps(doc))
