"""Metrics lane gates: quantitative models, budgets and the generated dashboard.

Tiers (see docs/metrics/README.md and ADR-0038):

* `metrics` (full): the STRUCTURAL profile only. Martin metrics, complexity and maintainability, static test
  inventory: deterministic functions of the source tree, no timing, no coverage run, no other lanes' reports.
  Fails on a structural budget FAIL or when the committed dashboard no longer renders from its snapshot.
* `metrics_report` (release): the machine-dependent evidence. Converts the quality lane's coverage data
  (run `nox -s coverage metrics_report` so it exists), takes the full measurement profile (latency, fitted
  models), evaluates every budget, renders a fresh dashboard into reports/metrics/, and runs the timing tests.
* `metrics_snapshot_fresh` (release): the committed snapshot's deterministic sections equal the current tree.

Committing a new platform-labelled snapshot is a deliberate act: `python -m quality.metrics snapshot`.
"""
import sys
from pathlib import Path

import nox

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False
ROOT = Path(__file__).resolve().parents[2]


def _env() -> dict[str, str]:
    """Keep every tool's scratch space inside the checkout: the system TEMP may be a slow HDD."""
    scratch = ROOT / ".tmp"
    scratch.mkdir(exist_ok=True)
    return {"TMP": str(scratch), "TEMP": str(scratch)}


@nox.session(python=False, tags=["full"])
def metrics(session: nox.Session) -> None:
    """Structural metrics (Martin, complexity, test inventory), structural budgets, dashboard renders from its snapshot."""
    session.run(PYTHON, "-m", "quality.metrics", "collect", "--profile", "structural", env=_env())
    session.run(PYTHON, "-m", "quality.metrics", "check", env=_env())
    session.run(PYTHON, "-m", "quality.metrics", "drift", env=_env())


@nox.session(python=False, tags=["release"])
def metrics_report(session: nox.Session) -> None:
    """Release evidence: coverage export, full-profile measurement (median and IQR), all budgets, dashboard in reports/metrics/."""
    session.run(PYTHON, "-m", "quality.metrics", "coverage", env=_env(), success_codes=[0, 1])  # 1 = NOT_RUN (no coverage data)
    session.run(PYTHON, "-m", "quality.metrics", "collect", "--profile", "full", env=_env())
    session.run(PYTHON, "-m", "quality.metrics", "check", env=_env())
    session.run(PYTHON, "-m", "quality.metrics", "render", env=_env())
    session.run(PYTHON, "-m", "pytest", "-q", "tests/metrics", env={**_env(), "EIJA_METRICS_TIMING": "1"})


@nox.session(python=False, tags=["release"])
def metrics_snapshot_fresh(session: nox.Session) -> None:
    """Release tier: the committed snapshot's deterministic sections describe the CURRENT source (strict drift check)."""
    session.run(PYTHON, "-m", "quality.metrics", "drift", "--strict", env=_env())
