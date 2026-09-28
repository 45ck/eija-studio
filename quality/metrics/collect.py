"""Orchestrate every collector into one document (schema `eija.metrics.v1`, see docs/metrics/README.md).

Top-level keys of `reports/metrics.json`:

    schema, meta{profile, platform, source{commit,dirty}, tools, timing_note, generated_at?},
    sections{martin, complexity, tests, coverage, lane_reports, performance, scaling, verification_yield},
    budgets[{id, description, actual, op, limit, status, kind, section}]

Every section has `status` MEASURED or NOT_RUN (+ `reason`). Sections `performance`, `scaling` and
`verification_yield` hold timing measurements; the rest are deterministic given the source tree.
"""
from __future__ import annotations

from . import ROOT
from . import aggregate, budgets, complexity, inventory, perf, scaling, structure
from .common import MEASURED, NOT_RUN, dumps, measured, meta, not_run, r3, write_text

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
                     "findings": matrix["oracle_mismatches"], "duration_s": r3(matrix["seconds"]),
                     "states_per_s": r3(matrix["cells"] / matrix["seconds"]), "accepted_cells": matrix["accepted"],
                     "denied_cells": matrix["denied"], "status": "MEASURED",
                     "note": "cells = actor x state x action; findings = oracle/runtime disagreements (same-author oracle)"})
    if impact:
        rows.append({"technique": "impact_closure (this kernel)", "kind": "measured-here", "states_explored": impact["nodes"],
                     "findings": None, "duration_s": r3(impact["seconds"]),
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


def collect(profile: str = "quick", *, generated_at: str | None = None, real_server: bool = True,
            pytest_collection: bool = True) -> dict:
    if profile not in perf.PROFILES:
        raise ValueError(f"unknown profile {profile!r}")
    sections = structural_sections(pytest_collection=pytest_collection)
    performance, yields = perf.collect(profile, real_server=real_server)
    sections["performance"] = performance
    sections["scaling"] = scaling.collect(profile)
    sections["verification_yield"] = yield_section(yields["matrix"], yields["impact"], sections["lane_reports"])
    doc = {"schema": meta(profile, generated_at)["schema"], "meta": meta(profile, generated_at), "sections": sections}
    doc["budgets"] = budgets.evaluate(doc)
    return doc


def write(doc: dict, path=REPORT) -> None:
    write_text(path, dumps(doc))
