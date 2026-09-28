"""Gates for the scripted demo recordings (ADR-0047, ADR-0048)."""
import importlib.util
import sys

import nox

PYTHON = sys.executable


@nox.session(python=False, tags=["fast", "full"])
def demos_registry(session: nox.Session) -> None:
    """Catalogue matches the code, REGISTRY.md is fresh, manifests are well formed. No browser needed."""
    session.run(PYTHON, "-m", "demos", "registry", "--check")
    session.run(PYTHON, "-m", "pytest", "-q", "tests/demo_catalogue", *session.posargs)


@nox.session(python=False, tags=["full"])
def demos_typecheck(session: nox.Session) -> None:
    """mypy over the demos package (the shared mypy config names only eija_studio); needs the demos extra."""
    if importlib.util.find_spec("playwright") is None:
        session.skip("NOT_RUN: the demos extra (playwright) is not installed, so its types cannot be checked")
    session.run(PYTHON, "-m", "mypy", "demos")


@nox.session(python=False, tags=["full"])
def demos_dry(session: nox.Session) -> None:
    """Every non-blocked scenario still works against the real Studio (no video).

    Reports NOT_RUN (the session is skipped, never passed) when Playwright is missing or the system
    Chrome cannot be launched (`python -m demos` exits 3). A scenario failing while it runs is a failure."""
    output = session.run(
        PYTHON, "-m", "demos", "run", "assurance_loop", "--dry-run", success_codes=[0, 3], silent=True
    )
    session.log(output or "")
    if "NOT_RUN" in (output or ""):
        session.skip("NOT_RUN: Playwright or Chrome is unavailable, so no scenario was exercised")


@nox.session(python=False, tags=["release"])
def demos_record(session: nox.Session) -> None:
    """Maintainer-only: record the scenarios (slow, needs Chrome and a free display/CPU)."""
    session.run(PYTHON, "-m", "demos", "run", "assurance_loop")
