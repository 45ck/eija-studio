"""CI cost and reliability budget (ADR-0228, amendment of 17 November 2026).

The repository is public, so GitHub's standard Linux runners cost nothing. These tests keep it that way and keep a
hung or repeated run from piling up minutes: every workflow must

* run only on a pinned standard Linux image (larger, macOS and Windows runners bill even for public repositories),
* give every job a timeout of at most 60 minutes (the default is 6 hours),
* cancel a superseded run on the same ref or pull request (``concurrency`` with ``cancel-in-progress``),
* pin every action to a full commit SHA, and
* schedule at most one run a day.

Each rule has a negative control: a planted workflow that breaks it must be caught.
"""

import re
from pathlib import Path

import pytest
import yaml  # PyYAML arrives with the lint extra (xenon), which the hosted fast tier installs

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = sorted((ROOT / ".github" / "workflows").glob("*.yml"))

STANDARD_RUNNERS = {"ubuntu-24.04"}
MAX_TIMEOUT_MINUTES = 60
SHA = re.compile(r"^[^@\s]+@[0-9a-f]{40}$")


def budget_problems(text: str) -> list[str]:
    """Every way one workflow breaks the CI budget, as sentences. Empty means within budget."""
    doc = yaml.safe_load(text)
    problems: list[str] = []
    triggers = doc.get("on", doc.get(True)) or {}
    if isinstance(triggers, (str, list)):
        triggers = dict.fromkeys([triggers] if isinstance(triggers, str) else triggers)
    concurrency = doc.get("concurrency")
    if not isinstance(concurrency, dict) or concurrency.get("cancel-in-progress") is not True:
        problems.append("workflow has no concurrency group with cancel-in-progress: true")
    for entry in triggers.get("schedule") or []:
        minute, hour = entry["cron"].split()[:2]
        if not (minute.isdigit() and hour.isdigit()):
            problems.append(f"schedule {entry['cron']!r} runs more than once a day")
    if len(triggers.get("schedule") or []) > 1:
        problems.append("more than one schedule")
    for name, job in (doc.get("jobs") or {}).items():
        runner = job.get("runs-on")
        if runner not in STANDARD_RUNNERS:
            problems.append(f"job {name}: runs-on {runner!r} is not one of {sorted(STANDARD_RUNNERS)}")
        timeout = job.get("timeout-minutes")
        if not isinstance(timeout, int) or timeout > MAX_TIMEOUT_MINUTES:
            problems.append(
                f"job {name}: timeout-minutes {timeout!r} is missing or over {MAX_TIMEOUT_MINUTES}"
            )
        for step in job.get("steps") or []:
            uses = step.get("uses")
            if uses and not uses.startswith("./") and not SHA.match(uses):
                problems.append(f"job {name}: action {uses!r} is not pinned to a commit SHA")
    return problems


def test_there_are_workflows_to_check():
    assert {path.name for path in WORKFLOWS} >= {"quality.yml", "guardrails.yml", "test.yml"}


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda path: path.name)
def test_every_workflow_is_within_the_ci_budget(path):
    assert budget_problems(path.read_text(encoding="utf-8")) == []


GOOD = """
on:
  pull_request:
  schedule:
    - cron: '17 15 * * *'
concurrency:
  group: x
  cancel-in-progress: true
jobs:
  fast:
    runs-on: ubuntu-24.04
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803
      - run: echo ok
"""


def test_the_control_workflow_is_within_budget():
    assert budget_problems(GOOD) == []


@pytest.mark.parametrize(
    ("old", "new", "expected"),
    [
        ("runs-on: ubuntu-24.04", "runs-on: macos-latest", "is not one of"),
        ("runs-on: ubuntu-24.04", "runs-on: ubuntu-latest-16-cores", "is not one of"),
        ("    timeout-minutes: 15\n", "", "timeout-minutes None is missing"),
        ("timeout-minutes: 15", "timeout-minutes: 360", "timeout-minutes 360 is missing or over"),
        ("cancel-in-progress: true", "cancel-in-progress: false", "no concurrency group"),
        ("@d23441a48e516b6c34aea4fa41551a30e30af803", "@v6", "is not pinned to a commit SHA"),
        ("'17 15 * * *'", "'*/30 * * * *'", "runs more than once a day"),
        (
            "    - cron: '17 15 * * *'",
            "    - cron: '17 15 * * *'\n    - cron: '17 3 * * *'",
            "more than one schedule",
        ),
    ],
)
def test_a_workflow_over_budget_is_caught(old, new, expected):
    assert old in GOOD
    problems = budget_problems(GOOD.replace(old, new))
    assert any(expected in problem for problem in problems), problems
