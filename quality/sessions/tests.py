"""Kernel regression suite."""
import sys
from pathlib import Path

import nox

from quality.tools.parallel import xdist_args

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False
JUNIT = Path("reports") / "testing" / "pytest-fast.xml"


# Tagged fast only: the `full` tier runs the same suite inside the `coverage` session, so tagging it here too
# ran the whole suite twice (about 2 minutes wasted on the reference PC).
@nox.session(python=False, tags=["fast"])
def tests(session: nox.Session) -> None:
    """Unit, integration, crash-recovery and concurrency tests of the kernel; then the skip ledger.

    A skipped test inside a green session is NOT_RUN that nox cannot see, so the run writes junit and
    quality/tools/skip_ledger.py fails on any skip the ledger does not record (a missing extra, a new importorskip).
    """
    JUNIT.parent.mkdir(parents=True, exist_ok=True)
    session.run(PYTHON, "-m", "pytest", "-q", f"--junitxml={JUNIT}", *xdist_args(), *session.posargs)
    session.run(PYTHON, "-m", "quality.tools.skip_ledger", str(JUNIT))


@nox.session(python=False, tags=["release"])
def release_fixture(session: nox.Session) -> None:
    """Owner-only release gate: current bytes must match the owner-stamped fixture. Agents never stamp."""
    session.run(PYTHON, "scripts/verify_release.py")
