"""Compare the pull-request states claimed in the roadmap and lane hubs with GitHub's live states.

What this establishes: every `open PR #n` / `merged PR #n` / `closed PR #n` phrase in README.md, docs/ROADMAP.md
and docs/lanes/*.md names a pull request whose live state (from `gh pr list`) is the one claimed.

What this does NOT establish: that the surrounding sentence is true, that a merged PR is on `main` at the
commit the page names, or anything about branches that have no pull request. Needs network and a logged-in
`gh`; without them it reports NOT_RUN (exit 2), never PASS.

    python scripts/check_pr_status.py       # exit 0 ok, 1 stale claim, 2 NOT_RUN
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAIM = re.compile(r"\b(open|merged|closed) PR #(\d+)", re.I)
NOT_RUN_EXIT = 2


def claim_files() -> list[Path]:
    return [ROOT / "README.md", ROOT / "docs/ROADMAP.md", *sorted((ROOT / "docs/lanes").glob("*.md"))]


def claims(text: str) -> list[tuple[str, int]]:
    """(claimed state, PR number) pairs in `text`, states upper-cased to match GitHub's."""
    return [(m.group(1).upper(), int(m.group(2))) for m in CLAIM.finditer(text)]


def stale(found: list[tuple[str, int]], live: dict[int, str]) -> list[str]:
    """Describe each claim whose PR is unknown or in a different state than claimed."""
    problems = []
    for state, number in sorted(set(found), key=lambda c: c[1]):
        if number not in live:
            problems.append(f"PR #{number} claimed {state} but GitHub lists no such pull request")
        elif live[number] != state:
            problems.append(f"PR #{number} claimed {state} but is {live[number]}")
    return problems


def live_states() -> dict[int, str] | None:
    """PR number -> OPEN/MERGED/CLOSED from `gh`, or None when gh is missing, logged out or offline."""
    gh = shutil.which("gh")
    if gh is None:
        return None
    done = subprocess.run([gh, "pr", "list", "--state", "all", "--limit", "500", "--json", "number,state"],
                          cwd=ROOT, capture_output=True, text=True, check=False, timeout=60)
    if done.returncode:
        return None
    return {int(row["number"]): str(row["state"]).upper() for row in json.loads(done.stdout)}


def main() -> int:
    found = [c for f in claim_files() for c in claims(f.read_bytes().decode("utf-8"))]
    live = live_states()
    if live is None:
        print(f"NOT_RUN pr status ({len(found)} claims unchecked): gh is missing, not logged in or offline")
        return NOT_RUN_EXIT
    problems = stale(found, live)
    for p in problems:
        print("STALE", p)
    print(f"{'FAIL' if problems else 'PASS'} pr status: {len(set(found))} distinct claims, {len(problems)} stale")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
