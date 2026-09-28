"""OSS lane gates: documentation, community files and README truthfulness (ADR-0043)."""
import importlib.util
import sys

import nox

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False


@nox.session(python=False, tags=["fast", "full"])
def docs_links(session: nox.Session) -> None:
    """Relative links and heading anchors in README, community files and docs/ resolve (offline)."""
    session.run(PYTHON, "scripts/check_doc_links.py")


@nox.session(python=False, tags=["fast", "full"])
def readme_diagram(session: nox.Session) -> None:
    """The README's before/after state diagram equals a fresh render of domain.policy."""
    session.run(PYTHON, "scripts/gen_readme_diagram.py", "--check")


@nox.session(python=False, tags=["fast", "full"])
def community_files(session: nox.Session) -> None:
    """Community files exist; CITATION.cff agrees with pyproject; roadmap covers all 13 lane ADR blocks."""
    session.run(PYTHON, "scripts/check_community_files.py")


@nox.session(python=False, tags=["release"])
def docs(session: nox.Session) -> None:
    """Build the MkDocs Material site with --strict. NOT_RUN when MkDocs (extra `docs`) is not installed."""
    if importlib.util.find_spec("mkdocs") is None or importlib.util.find_spec("material") is None:
        session.skip("NOT_RUN: mkdocs / mkdocs-material not installed (pip install -e '.[docs]')")
    session.run(PYTHON, "-m", "mkdocs", "build", "--strict", env={"NO_MKDOCS_2_WARNING": "true"})
