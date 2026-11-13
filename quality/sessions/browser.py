"""Opt-in PlayIDE browser and slow tests: the ones every other tier deselects.

The default pytest selection (`pyproject.toml`) excludes `slow`, and the PlayIDE browser tests skip unless
`EIJA_BROWSER_TESTS=1`. Before this session only `metrics` (tests/metrics) and `diagrams_syntax` (tests/test_syntax_validator.py)
selected either marker, so 116 tests in 31 files (the real-browser PlayIDE walks, the exact-app journey and the 26 seeded
conformance divergences) ran in no tier at all (counted on 2026-11-13).

    nox -s browser_suite                  # release tier; needs Playwright (the demos or hci extra) and a Chromium
    EIJA_CHROMIUM=/path/to/chrome nox -s browser_suite

Without Playwright every test would skip and the session would look green, so it fails with NOT_RUN instead, unless
EIJA_ALLOW_NOT_RUN=1 accepts the gap (then it skips and says NOT_RUN).
"""
import importlib.util
import os
import sys

import nox

from quality.tools.parallel import xdist_args

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False
# Run by their own sessions: the metrics lane's slow and timing tests, and the renderer checks of diagrams_syntax.
OWNED_ELSEWHERE = ("--ignore=tests/metrics", "--deselect=tests/test_syntax_validator.py")


@nox.session(python=False, tags=["release"])
def browser_suite(session: nox.Session) -> None:
    """Every `slow` or `browser` test outside tests/metrics, with EIJA_BROWSER_TESTS=1."""
    if importlib.util.find_spec("playwright") is None:
        message = "NOT_RUN: Playwright is not installed (pip install -e '.[demos]'), so no browser test ran. This is not a PASS."
        if os.environ.get("EIJA_ALLOW_NOT_RUN") == "1":
            session.skip(message)
        session.error(message + " Set EIJA_ALLOW_NOT_RUN=1 to record it as an accepted gap.")
    session.run(PYTHON, "-m", "pytest", "-q", "-rfEs", "-m", "slow or browser", *OWNED_ELSEWHERE, *xdist_args(),
                *session.posargs, env={"EIJA_BROWSER_TESTS": "1"})
