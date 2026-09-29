"""Aggregate the reports other capability lanes write under reports/ (read-only, never invented).

Convention (documented in docs/metrics/README.md): a lane report is a JSON object. This module reads
only what is there. The status comes from a top-level `status` or `verdict` (the formal lanes write
`verdict`, schema `eija.formal-report/v1`); a report with neither but with a `budgets` list (the hci
lane) is reduced from those budgets by a stated rule (any FAIL is FAIL, else any NOT_RUN is NOT_RUN,
else PASS; GAP, the hci lane's documented shortfall, is counted and never promoted). Anything else is
UNKNOWN, never PASS. A small vocabulary of numeric fields (at the top level, one level down, or summed
over `results.models[*]`) is mapped to canonical names. A missing directory or file is a NOT_RUN entry
with the reason, so an absent lane can never look green.

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
STATUSES = {"PASS", "FAIL", "NOT_RUN", "INCONCLUSIVE"}  # INCONCLUSIVE: a bounded search hit its cap (bmc); kept verbatim
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
SEVERITY = {"FAIL": 4, "UNREADABLE": 3, "UNKNOWN": 3, "INCONCLUSIVE": 3, "NOT_RUN": 2, "PASS": 1}  # worst first


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


def _model_states(doc: Any) -> int | None:
    """Sum of `results.models[*].states` (the bounded-model-check report shape), or None."""
    models = (doc.get("results") or {}).get("models") if isinstance(doc, dict) and isinstance(doc.get("results"), dict) else None
    counts = [_number(m.get("states")) for m in models.values() if isinstance(m, dict)] if isinstance(models, dict) else []
    counts = [c for c in counts if c is not None]
    return int(sum(counts)) if counts else None


def _status_of(doc: Any) -> tuple[str, str]:
    """(status, source). Copied verbatim from `status`/`verdict`; reduced from `budgets` only when neither exists."""
    if not isinstance(doc, dict):
        return "UNKNOWN", "none"
    for key in ("status", "verdict"):
        if isinstance(doc.get(key), str):
            value = doc[key].upper()
            return (value if value in STATUSES else "UNKNOWN"), key
    budgets = doc.get("budgets")
    if isinstance(budgets, list) and budgets and all(isinstance(b, dict) and isinstance(b.get("status"), str) for b in budgets):
        seen = {b["status"].upper() for b in budgets}
        return ("FAIL" if "FAIL" in seen else "NOT_RUN" if "NOT_RUN" in seen else "PASS"), "budgets"
    return "UNKNOWN", "none"


def read_report(path: Path) -> dict:
    raw = path.read_bytes()
    entry: dict[str, Any] = {"file": rel(path), "sha256": hashlib.sha256(raw).hexdigest()}
    try:
        doc = json.loads(raw)
    except ValueError as exc:
        return {**entry, "status": "UNREADABLE", "reason": f"invalid JSON: {exc.__class__.__name__}"}
    entry["status"], entry["status_source"] = _status_of(doc)
    label = next((doc[k] for k in ("technique", "kind") if isinstance(doc, dict) and isinstance(doc.get(k), str)), None)
    if label:
        entry["technique"] = label
    entry["values"] = extract(doc)
    states = _model_states(doc)
    if states is not None and "states_explored" not in entry["values"]:
        entry["values"]["states_explored"] = states
    if isinstance(doc, dict) and isinstance(doc.get("measurements"), dict):
        seconds = _number(doc["measurements"].get("seconds_total"))
        if seconds is not None and "duration_s" not in entry["values"]:
            entry["values"]["duration_s"] = seconds
    return entry


def _worst(entries: list[dict]) -> str:
    return max((e["status"] for e in entries), key=lambda st: SEVERITY.get(st, 3))


def collect(reports: Path = REPORTS) -> dict:
    groups = []
    for name, (pattern, lane, _expectation) in sorted(GROUPS.items()):
        files = sorted(reports.glob(pattern)) if reports.exists() else []
        if not files:
            groups.append({"group": name, "lane": lane, "status": NOT_RUN,
                           "reason": f"no reports/{pattern} (lane not run on this checkout)", "reports": []})
            continue
        entries = [read_report(f) for f in files]
        groups.append({"group": name, "lane": lane, "status": _worst(entries), "reports": entries})
    present = sum(g["status"] != NOT_RUN for g in groups)
    return measured(
        method="read reports/{formal,mutation,testing,hci}; statuses copied verbatim (or reduced from budgets, stated), never inferred",
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
