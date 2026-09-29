"""Metrics lane gates: quantitative models, budgets and the generated dashboard.

`metrics` (full) runs the quick profile, fails on any STRUCTURAL budget FAIL or on drift between the
committed snapshot and its rendered dashboard, and runs the slow and wall-clock tests of the lane (once more
on failure). Timing budgets are printed as advisory there: a busy shared PC must not turn the gate red.
`metrics_report` (release) runs the suite under coverage, measures the full profile with one timing
re-measurement, enforces every budget including timing, requires the snapshot to be fresh, and renders a
dashboard into reports/metrics/. Committing a new snapshot is a deliberate act: `python -m quality.metrics snapshot`.
"""
import subprocess
import sys

import nox

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False
SLOW_TESTS = (PYTHON, "-m", "pytest", "-q", "-m", "slow or timing", "tests/metrics")


@nox.session(python=False, tags=["full"])
def metrics(session: nox.Session) -> None:
    """Collect metrics (quick profile), gate structural budgets, verify the dashboard is not stale."""
    session.run(PYTHON, "-m", "quality.metrics", "collect", "--profile", "quick")
    session.run(PYTHON, "-m", "quality.metrics", "check", "--fail-on", "structural")
    session.run(PYTHON, "-m", "quality.metrics", "drift")
    # Slow tests start a real server and wall-clock assertions can flake under load: retry the failures once.
    if subprocess.run(SLOW_TESTS, check=False).returncode != 0:
        session.log("slow/timing tests failed; re-running the failures once")
        session.run(*SLOW_TESTS, "--last-failed", "--last-failed-no-failures", "none")


@nox.session(python=False, tags=["release"])
def metrics_report(session: nox.Session) -> None:
    """Release evidence: coverage run, full-profile measurement, all budgets, fresh snapshot, dashboard in reports/metrics/."""
    session.run(PYTHON, "-m", "quality.metrics", "coverage")
    session.run(PYTHON, "-m", "quality.metrics", "collect", "--profile", "full", "--timing-retries", "1")
    session.run(PYTHON, "-m", "quality.metrics", "check", "--fail-on", "all")
    session.run(PYTHON, "-m", "quality.metrics", "drift", "--freshness", "require")
    session.run(PYTHON, "-m", "quality.metrics", "render")
