"""HCI budgets as data + evaluator (used by the pytest marker `hci`).

Each budget has a `target` (the law's threshold: what the UI should reach) and a `limit` (the ratchet:
the worst value the current UI is allowed to have). Status:

    PASS     value <= target
    GAP      target < value <= limit   known, documented shortfall (pytest reports it as xfail, not pass)
    FAIL     value > limit             regression (pytest fails)
    NOT_RUN  the metric could not be measured

The visual lane tightens `limit` towards `target` as it applies docs/hci/REPORT.md recommendations;
budgets.json never loosens silently: a change to a limit is a reviewed diff.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BUDGETS_PATH = Path(__file__).with_name("budgets.json")


def load(path: Path = BUDGETS_PATH) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))["budgets"]


def lookup(report: dict, dotted: str) -> Any:
    node: Any = report
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def evaluate(report: dict, budgets: list[dict] | None = None) -> list[dict]:
    """Evaluate every budget against a report. Pure; does not read the browser."""
    out = []
    for b in budgets if budgets is not None else load():
        value = lookup(report, b["path"])
        if value is None:
            status = "NOT_RUN"
        elif value > b["limit"]:
            status = "FAIL"
        elif value > b["target"]:
            status = "GAP"
        else:
            status = "PASS"
        out.append({"id": b["id"], "law": b["law"], "path": b["path"], "unit": b["unit"], "value": value,
                    "target": b["target"], "limit": b["limit"], "status": status, "note": b.get("note", "")})
    return out
