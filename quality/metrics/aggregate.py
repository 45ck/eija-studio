"""Aggregate the reports other capability lanes write under reports/ (read-only, never invented).

Convention (documented in docs/metrics/README.md): a lane report is a JSON object. This module reads
only what is there: a top-level verdict (`status`, else `verdict`, else a string `result`; PASS / FAIL / NOT_RUN,
anything else is reported as UNKNOWN, never promoted to PASS; the formal-report and TLA+ lanes write `verdict`
and `result`) and, at the top level or one level down (`summary`, `metrics`,
`result`, `totals`), a small vocabulary of numeric fields mapped to canonical names. A missing
directory or file is a NOT_RUN entry with the reason, so an absent lane can never look green.

Verification yield (states explored per technique) is derived only from reports that carry a
states-explored figure; the runtime-matrix and impact-closure rows are measured by this lane's own
performance collector and merged in by `collect.py`.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from . import ROOT
from .common import NOT_RUN, measured, r3, rel

REPORTS = ROOT / "reports"
GROUPS = {  # group -> (glob relative to reports/, owning lane, what a report there is expected to be)
    "formal": ("formal/*.json", "formal (Bend / TLA+ / Z3 / BMC)", "one JSON file per technique"),
    "mutation": ("mutation/summary.json", "mutation", "mutation score summary"),
    "testing": ("testing/*.json", "testing", "property/model-based test summaries"),
    "hci": ("hci/*.json", "hci", "usability and accessibility summaries"),
}
STATUSES = {"PASS", "FAIL", "NOT_RUN"}
CANONICAL = {  # canonical field -> accepted spellings, in priority order
    "states_explored": ("states_explored", "distinct_states", "states", "explored_states", "states_checked"),
    "checks": ("checks", "total_checks", "properties_checked", "examples", "cases"),
    "findings": ("counterexamples", "findings", "failures", "violations"),
    "duration_s": ("duration_s", "seconds", "elapsed_s", "duration_seconds"),
    "mutation_score": ("mutation_score", "score"),
    "mutants": ("mutants", "total_mutants", "total"),
    "killed": ("killed",),
    "survived": ("survived",),
}
NESTED = ("summary", "metrics", "result", "totals")


def _number(value: Any) -> float | int | None:
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def extract(doc: Any) -> dict:
    """Pull canonical numeric fields out of a lane report; unknown shapes yield an empty dict."""
    if not isinstance(doc, dict):
        return {}
    scopes = [doc] + [doc[k] for k in NESTED if isinstance(doc.get(k), dict)]
    found: dict[str, float | int] = {}
    for canon, spellings in CANONICAL.items():
        for scope in scopes:
            hit = next((n for n in (_number(scope.get(s)) for s in spellings) if n is not None), None)
            if hit is not None:
                found[canon] = hit
                break
    return found


VERDICT_FIELDS = ("status", "verdict", "result")


def _verdict(doc: Any) -> str:
    """The lane's own verdict, verbatim: the first of `status`, `verdict`, `result` that holds a string (else empty)."""
    if not isinstance(doc, dict):
        return ""
    return next((v.upper() for v in (doc.get(k) for k in VERDICT_FIELDS) if isinstance(v, str)), "")


def read_report(path: Path) -> dict:
    raw = path.read_bytes()
    entry: dict[str, Any] = {"file": rel(path), "sha256": hashlib.sha256(raw).hexdigest()}
    try:
        doc = json.loads(raw)
    except ValueError as exc:
        return {**entry, "status": "UNREADABLE", "reason": f"invalid JSON: {exc.__class__.__name__}"}
    status = _verdict(doc)
    entry["status"] = status if status in STATUSES else "UNKNOWN"
    if isinstance(doc, dict) and isinstance(doc.get("technique"), str):
        entry["technique"] = doc["technique"]
    entry["values"] = extract(doc)
    return entry


def _worst(entries: list[dict]) -> str:
    """The weakest report decides: FAIL, then UNKNOWN (unreadable included), then NOT_RUN, else PASS."""
    statuses = {e["status"] for e in entries}
    if "FAIL" in statuses:
        return "FAIL"
    if statuses & {"UNKNOWN", "UNREADABLE"}:
        return "UNKNOWN"
    return "NOT_RUN" if "NOT_RUN" in statuses else "PASS"


def _group(name: str, pattern: str, lane: str, reports: Path) -> dict:
    files = sorted(reports.glob(pattern)) if reports.exists() else []
    if not files:
        return {"group": name, "lane": lane, "status": NOT_RUN,
                "reason": f"no reports/{pattern} (lane not run on this checkout)", "reports": []}
    entries = [read_report(f) for f in files]
    return {"group": name, "lane": lane, "status": _worst(entries), "reports": entries}


def collect(reports: Path = REPORTS) -> dict:
    groups = [_group(name, pattern, lane, reports) for name, (pattern, lane, _expectation) in sorted(GROUPS.items())]
    present = sum(g["status"] != NOT_RUN for g in groups)
    return measured(
        method="read reports/{formal,mutation,testing,hci}; statuses copied verbatim, never inferred",
        not_measured=["the correctness of any lane's report (this module aggregates, it does not re-verify)"],
        groups=groups, summary={"groups": len(groups), "groups_with_reports": present,
                                "groups_not_run": len(groups) - present})


def yield_rows(aggregated: dict) -> list[dict]:
    """Verification yield from lane reports that expose a states-explored figure."""
    rows = []
    for group in aggregated.get("groups", []):
        for rep in group["reports"]:
            v = rep.get("values", {})
            if "states_explored" not in v:
                continue
            states, seconds = v["states_explored"], v.get("duration_s")
            rows.append({"technique": rep.get("technique") or Path(rep["file"]).stem, "source": rep["file"],
                         "kind": "lane-report", "states_explored": states, "findings": v.get("findings"),
                         "duration_s": seconds, "states_per_s": r3(states / seconds) if seconds else None,
                         "status": rep["status"]})
    return sorted(rows, key=lambda r: (r["technique"], r["source"]))
