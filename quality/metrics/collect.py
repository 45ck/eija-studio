"""Orchestrate every collector into one document (schema `eija.metrics.v1`, see docs/metrics/README.md).

Top-level keys of `reports/metrics.json`:

    schema, meta{profile, platform, source{commit,dirty}, tools, timing_note, generated_at?},
    sections{martin, complexity, tests, coverage, lane_reports, performance, scaling, verification_yield},
    budgets[{id, description, actual, op, limit, status, kind, section}]

Every section has `status` MEASURED or NOT_RUN (+ `reason`). Sections `performance`, `scaling` and
`verification_yield` hold timing measurements; the rest are deterministic given the source tree.

Profiles: `structural` measures only what is a deterministic function of the tree (martin, complexity, the
static test inventory) and reports every machine-dependent section (timing, coverage, other lanes' reports)
as NOT_RUN "not collected in this profile". It is what the fast/full tiers run: no number in it depends on
the machine or on what else ran. `quick` and `full` add timing, coverage and lane reports (release tier);
`smoke` is the pipeline check used by unit tests.
"""
from __future__ import annotations

from . import ROOT, aggregate, budgets, complexity, inventory, perf, scaling, structure
from .common import dumps, measured, meta, not_run, r3, write_text

REPORT = ROOT / "reports" / "metrics.json"
DETERMINISTIC = ("martin", "complexity", "tests")  # sections that are a pure function of the source tree
STRUCTURAL = "structural"
PROFILES = (STRUCTURAL, *perf.PROFILES)
NOT_COLLECTED = "not collected in the structural profile: machine-dependent evidence is release-tier (`nox -s metrics_report`)"


def structural_sections(*, pytest_collection: bool = True) -> dict:
    """The deterministic sections only (no timing, no coverage, no other lanes' reports)."""
    return {"martin": structure.collect(), "complexity": complexity.collect(),
            "tests": inventory.collect(run_pytest_collection=pytest_collection)}


def _matrix_row(matrix: dict) -> dict:
    return {"technique": "runtime_matrix (this kernel)", "kind": "measured-here", "states_explored": matrix["cells"],
            "findings": matrix["oracle_mismatches"], "duration_s": round(matrix["seconds"], 4),
            "states_per_s": r3(matrix["cells"] / matrix["seconds"]), "accepted_cells": matrix["accepted"],
            "denied_cells": matrix["denied"], "status": "MEASURED",
            "note": ("cells = actor x state x action; findings = oracle/runtime disagreements (same-author oracle); "
                     "duration = median of the repeats")}


def _impact_row(impact: dict) -> dict:
    return {"technique": "impact_closure (this kernel)", "kind": "measured-here", "states_explored": impact["nodes"],
            "findings": None, "duration_s": round(impact["seconds"], 7),
            "states_per_s": r3(impact["nodes"] / impact["seconds"]), "status": "MEASURED",
            "note": "nodes of the projection-dependency graph reached from the changed actions; duration = median of 15 repeats"}


def yield_section(matrix: dict, impact: dict, lanes: dict) -> dict:
    rows = ([_matrix_row(matrix)] if matrix else []) + ([_impact_row(impact)] if impact else []) + aggregate.yield_rows(lanes)
    lane_rows = [r for r in rows if r["kind"] == "lane-report"]
    reports = sum(len(g["reports"]) for g in lanes.get("groups", []))
    return measured(
        kind="measurement", method="states explored per technique: two measured here, the rest copied from lane reports",
        not_measured=["independence of techniques", "defect-finding power (findings are counts reported by each technique)"],
        techniques=rows, summary={"techniques": len(rows), "from_lane_reports": len(lane_rows),
                                  "lane_reports_without_state_counts": max(0, reports - len(lane_rows))})


def _release_sections(profile: str, real_server: bool) -> dict:
    lanes = aggregate.collect()
    performance, yields = perf.collect(profile, real_server=real_server)
    return {"coverage": inventory.collect_coverage(), "lane_reports": lanes, "performance": performance,
            "scaling": scaling.collect(profile), "verification_yield": yield_section(yields["matrix"], yields["impact"], lanes)}


def _skipped_sections() -> dict:
    return {name: not_run(NOT_COLLECTED) for name in ("coverage", "lane_reports", "performance", "scaling", "verification_yield")}


def collect(profile: str = STRUCTURAL, *, generated_at: str | None = None, real_server: bool = True) -> dict:
    if profile not in PROFILES:
        raise ValueError(f"unknown profile {profile!r}")
    structural = profile == STRUCTURAL
    sections = structural_sections(pytest_collection=not structural)
    sections |= _skipped_sections() if structural else _release_sections(profile, real_server)
    doc = {"schema": meta(profile, generated_at)["schema"], "meta": meta(profile, generated_at), "sections": sections}
    doc["budgets"] = budgets.evaluate(doc)
    return doc


def write(doc: dict, path=REPORT) -> None:
    write_text(path, dumps(doc))
