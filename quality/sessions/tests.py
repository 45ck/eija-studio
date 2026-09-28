"""Kernel regression suite."""
import sys

import nox

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False


@nox.session(python=False, tags=["fast", "full"])
def tests(session: nox.Session) -> None:
    """Unit, integration, crash-recovery and concurrency tests of the kernel."""
    session.run(PYTHON, "-m", "pytest", "-q", *session.posargs)


@nox.session(python=False, tags=["release"])
def release_fixture(session: nox.Session) -> None:
    """Owner-only release gate: current bytes must match the owner-stamped fixture. Agents never stamp."""
    session.run(PYTHON, "scripts/verify_release.py")
