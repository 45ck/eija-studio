"""Repository hygiene gates: generated indexes must not drift."""
import sys

import nox

PYTHON = sys.executable


@nox.session(python=False, tags=["fast", "full"])
def adr_index(session: nox.Session) -> None:
    """docs/adr/README.md index matches the ADR files; numbers unique; every record parses."""
    session.run(PYTHON, "-m", "quality.tools.adr_index", "--check")
    session.run(PYTHON, "-m", "pytest", "-q", "tests/tools", *session.posargs)
