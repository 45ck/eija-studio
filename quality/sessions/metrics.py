"""Metrics lane gates: quantitative models, budgets and the generated dashboard.

`metrics` (full) runs the quick profile and fails on any budget FAIL or on drift between the
committed snapshot and its rendered dashboard. `metrics_report` (release) runs the suite under
coverage, takes the full measurement profile and renders a fresh dashboard into reports/metrics/.
Committing a new platform-labelled snapshot is a deliberate act: `python -m quality.metrics snapshot`.
"""
import sys

import nox

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False


@nox.session(python=False, tags=["full"])
def metrics(session: nox.Session) -> None:
    """Collect metrics (quick profile), evaluate budgets, verify the committed dashboard is not stale."""
    session.run(PYTHON, "-m", "quality.metrics", "collect", "--profile", "quick")
    session.run(PYTHON, "-m", "quality.metrics", "check")
    session.run(PYTHON, "-m", "quality.metrics", "drift")


@nox.session(python=False, tags=["release"])
def metrics_report(session: nox.Session) -> None:
    """Release evidence: coverage run, full-profile measurement, budgets, dashboard in reports/metrics/."""
    session.run(PYTHON, "-m", "quality.metrics", "coverage")
    session.run(PYTHON, "-m", "quality.metrics", "collect", "--profile", "full")
    session.run(PYTHON, "-m", "quality.metrics", "check")
    session.run(PYTHON, "-m", "quality.metrics", "render")
