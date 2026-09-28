"""OSS lane gates: documentation, community files and README truthfulness (ADR-0043)."""
import importlib.util
import subprocess
import sys
from pathlib import Path

import nox

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False
ROOT = Path(__file__).resolve().parents[2]
NOT_RUN_EXIT = 2  # exit code scripts/check_community_files.py uses for "nothing failed, something could not run"


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
    """Community files exist; CITATION.cff agrees with pyproject; roadmap covers every reserved ADR block.

    NOT_RUN (a skipped session, never a green one) when PyYAML (extra `docs`) is missing and the issue forms
    could not be parsed; every other check still ran and its failures still fail the session.
    """
    result = subprocess.run([PYTHON, "scripts/check_community_files.py"], cwd=ROOT, check=False)
    if result.returncode == NOT_RUN_EXIT:
        session.skip("NOT_RUN: issue-form parse needs PyYAML (pip install -e '.[docs]'); the other checks passed")
    if result.returncode:
        session.error(f"check_community_files.py exited {result.returncode}")


@nox.session(python=False, tags=["release"])
def docs(session: nox.Session) -> None:
    """Build the MkDocs Material site with --strict. NOT_RUN when MkDocs (extra `docs`) is not installed."""
    if importlib.util.find_spec("mkdocs") is None or importlib.util.find_spec("material") is None:
        session.skip("NOT_RUN: mkdocs / mkdocs-material not installed (pip install -e '.[docs]')")
    session.run(PYTHON, "-m", "mkdocs", "build", "--strict", env={"NO_MKDOCS_2_WARNING": "true"})


@nox.session(python=False, tags=["release"])
def pr_status(session: nox.Session) -> None:
    """Pull-request states claimed in the roadmap and lane hubs equal GitHub's. NOT_RUN without `gh` and network."""
    result = subprocess.run([PYTHON, "scripts/check_pr_status.py"], cwd=ROOT, check=False)
    if result.returncode == NOT_RUN_EXIT:
        session.skip("NOT_RUN: needs a logged-in gh CLI and network")
    if result.returncode:
        session.error(f"check_pr_status.py exited {result.returncode}")
