"""Read a `nox --report` file and say which sessions did not run.

nox exits 0 when a session calls `session.skip()`, so a tier whose gates all skipped for a missing extra or tool looks the
same as a tier that passed (docs/quality/gates.md, "Missing prerequisites report NOT_RUN, never PASS"). The hosted
workflow is such an aggregator: it reads only the exit code. This reads the report instead.

    python -m quality.tools.nox_report reports/nox-fast.json --fail-on-skip   # the fast tier must run every gate
    python -m quality.tools.nox_report reports/nox-full.json                  # list NOT_RUN sessions, exit 0

With `GITHUB_STEP_SUMMARY` set, the summary is also appended there, so a hosted run shows its NOT_RUN gates.
"""

# ruff: noqa: T201
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def summarise(report: dict) -> tuple[list[str], list[str], list[tuple[str, str]]]:
    """(passed, failed, skipped with reason) session names from a nox report."""
    passed, failed, skipped = [], [], []
    for entry in report.get("sessions", []):
        name, result = entry.get("name", "?"), entry.get("result")
        if result == "success":
            passed.append(name)
        elif result == "skipped":
            skipped.append((name, entry.get("reason") or "no reason given"))
        else:
            failed.append(name)
    return passed, failed, skipped


def render(passed: list[str], failed: list[str], skipped: list[tuple[str, str]]) -> str:
    lines = [f"nox: {len(passed)} passed, {len(failed)} failed, {len(skipped)} NOT_RUN (skipped)"]
    lines += [f"- NOT_RUN {name}: {reason}" for name, reason in skipped]
    lines += [f"- FAILED {name}" for name in failed]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("report", type=Path)
    parser.add_argument("--fail-on-skip", action="store_true", help="exit 1 when any session was skipped (NOT_RUN)")
    args = parser.parse_args(argv)
    try:
        report = json.loads(args.report.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"NOT_RUN: no readable nox report at {args.report}: {exc}")
        return 1
    passed, failed, skipped = summarise(report)
    text = render(passed, failed, skipped)
    print(text)
    if summary := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write(text + "\n")
    if not (passed or failed or skipped):
        print("NOT_RUN: the report lists no sessions")
        return 1
    return 1 if failed or (skipped and args.fail_on_skip) else 0


if __name__ == "__main__":
    sys.exit(main())
