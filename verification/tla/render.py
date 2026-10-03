"""Turn a TLC counterexample into a readable step list.

TLC prints each counterexample state as the values of the spec variables (`st`, `ver`, `ops`, `audit`,
`outbox`, `dir`, `emitted`). This module diffs consecutive states to say what each step did. It
interprets TLC output; it does not decide whether anything is a violation.
"""
from __future__ import annotations

from typing import Any

from .model import TlaConfig, transition_table


def describe_steps(config: TlaConfig, trace: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One record per counterexample state: {n, step, state, version, audit, outbox, effects_emitted}."""
    table = transition_table(config.workflow)
    rows: list[dict[str, Any]] = []
    previous: dict[str, Any] | None = None
    for n, now in enumerate(trace, start=1):
        rows.append({"n": n, "step": _step_text(previous, now, table), "state": now["st"], "version": now["ver"],
                     "audit": now["audit"], "outbox": {op: c for op, c in sorted(now["outbox"].items()) if c},
                     "effects_emitted": sorted(now.get("emitted", ()))})
        previous = now
    return rows


def _step_text(before: dict[str, Any] | None, now: dict[str, Any], table: dict[str, Any]) -> str:
    if before is None:
        return "initial state (Draft, version 0, fixture directory)"
    for actor, new in sorted(now["dir"].items()):
        for field in ("active", "assigned"):
            if before["dir"][actor][field] != new[field]:
                return f"environment: directory sets {actor}.{field} = {new[field]}"
    for op, new in sorted(now["ops"].items()):
        old = before["ops"][op]
        if new["used"] and new != old:
            src = table.get(new["action"], {}).get("src", "?")
            return (f"{new['actor']} executes {new['action']} as {op} (expectedVersion {new['ver']}): "
                    f"{src} -> {new['res'][0]}, version {new['res'][1]}")
    for op, count in sorted(now["outbox"].items()):
        if count != before["outbox"][op]:
            return f"replay of {op} re-queued its effects (outbox rows {before['outbox'][op]} -> {count}, audit {before['audit']} -> {now['audit']})"
    return "state changed"


def markdown(name: str, violated: str, description: str, rows: list[dict[str, Any]], note: str = "") -> str:
    lines = [f"### {name}", "", description, "", f"TLC reports `{violated}` violated after {len(rows)} states.", "", *([note, ""] if note else []),
             "| # | step | workflow state | version | audit | outbox rows |", "|---|---|---|---|---|---|"]
    for r in rows:
        outbox = ", ".join(f"{k}={v}" for k, v in r["outbox"].items()) or "-"
        lines.append(f"| {r['n']} | {r['step']} | {r['state']} | {r['version']} | {r['audit']} | {outbox} |")
    return "\n".join(lines) + "\n"
