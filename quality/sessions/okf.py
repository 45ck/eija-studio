"""Knowledge-base gates: the OKF v0.2 wiki under okf/ must be conformant, navigable and linked to current code."""
import importlib.util
import sys
from pathlib import Path

import nox

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False
REQUIRED = {"frontmatter": "python-frontmatter", "yaml": "PyYAML", "markdown_it": "markdown-it-py"}


def _require_extra(session: nox.Session) -> None:
    missing = [dist for module, dist in REQUIRED.items() if importlib.util.find_spec(module) is None]
    if missing:
        session.skip(f"NOT_RUN: install the okf extra (pip install -e .[okf]); missing {', '.join(missing)}")


@nox.session(python=False, tags=["fast", "full"])
def okf(session: nox.Session) -> None:
    """OKF v0.2 conformance, internal links, code-link hashes (STALE), coverage and generator drift.

    Fix a STALE or DRIFT finding by reviewing the listed pages and running `python -m quality.okf sync`.
    A PASS establishes that the wiki is well-formed and baselined against today's code, not that any
    page's prose is correct. Missing tooling reports NOT_RUN (a skipped session), never PASS.
    """
    _require_extra(session)
    session.run(PYTHON, "-m", "quality.okf", "check")


@nox.session(python=False, tags=["full"])
def okf_tools(session: nox.Session) -> None:
    """Tests of the OKF tooling itself: hash normalisation, marker-preserving regeneration, and a negative control per check."""
    _require_extra(session)
    # Outside tests/ on purpose: the kernel suite (`pytest -q`) stays fast and free of this lane's dependencies.
    Path(".pytest-tmp").mkdir(exist_ok=True)   # pytest creates only the last path component of --basetemp
    session.run(PYTHON, "-m", "pytest", "-q", "quality/okf/tests", "--basetemp=.pytest-tmp/okf", *session.posargs)
