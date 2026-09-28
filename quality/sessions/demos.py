"""Gates for the scripted demo recordings (ADR-0047, ADR-0048)."""
import sys

import nox

PYTHON = sys.executable


@nox.session(python=False, tags=["fast", "full"])
def demos_registry(session: nox.Session) -> None:
    """Catalogue is consistent with the code and REGISTRY.md is not stale. No browser needed."""
    session.run(PYTHON, "-m", "demos", "registry", "--check")
    session.run(PYTHON, "-m", "pytest", "-q", "tests/demo_catalogue", *session.posargs)


@nox.session(python=False, tags=["full"])
def demos_dry(session: nox.Session) -> None:
    """Every non-blocked scenario still works against the real Studio (no video). NOT_RUN without Chrome."""
    session.run(PYTHON, "-m", "demos", "run", "assurance_loop", "--dry-run")


@nox.session(python=False, tags=["release"])
def demos_record(session: nox.Session) -> None:
    """Maintainer-only: record the scenarios (slow, needs Chrome and a free display/CPU)."""
    session.run(PYTHON, "-m", "demos", "run", "assurance_loop")
