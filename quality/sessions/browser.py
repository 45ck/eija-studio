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

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False
# Run by their own sessions: the metrics lane's slow and timing tests, and the renderer checks of diagrams_syntax.
OWNED_ELSEWHERE = ("--ignore=tests/metrics", "--deselect=tests/test_syntax_validator.py")


# The same launch the browser tests make (EIJA_CHROMIUM, else the installed Chrome). They skip when it fails, so without
# this probe a run with Playwright but no browser would pass on the non-browser slow tests alone.
LAUNCH_PROBE = """
import os, sys
from playwright.sync_api import Error, sync_playwright
try:
    with sync_playwright() as p:
        exe = os.environ.get("EIJA_CHROMIUM")
        browser = p.chromium.launch(headless=True, **({"executable_path": exe} if exe else {"channel": "chrome"}))
        browser.close()
except Error as exc:
    print(str(exc).splitlines()[0])
    sys.exit(3)
"""


def _not_run(session: nox.Session, message: str) -> None:
    message = f"NOT_RUN: {message}, so no browser test ran. This is not a PASS."
    if os.environ.get("EIJA_ALLOW_NOT_RUN") == "1":
        session.skip(message)
    session.error(message + " Set EIJA_ALLOW_NOT_RUN=1 to record it as an accepted gap.")


@nox.session(python=False, tags=["release"])
def browser_suite(session: nox.Session) -> None:
    """Every `slow` or `browser` test outside tests/metrics, with EIJA_BROWSER_TESTS=1."""
    if importlib.util.find_spec("playwright") is None:
        _not_run(session, "Playwright is not installed (pip install -e '.[demos]')")
    reason = session.run(PYTHON, "-c", LAUNCH_PROBE, silent=True, success_codes=[0, 3])  # output; empty when it started
    if isinstance(reason, str) and reason.strip():
        _not_run(session, f"Chrome could not start ({reason.strip()}; set EIJA_CHROMIUM to a Chromium)")
    # Serial on purpose: one browser at a time (CONTRIBUTING.md). Under `-n 4` a Chromium per worker made
    # test_play_place's inline-edit walk time out, though it passes alone.
    session.run(PYTHON, "-m", "pytest", "-q", "-rfEs", "-m", "slow or browser", *OWNED_ELSEWHERE, *session.posargs,
                env={"EIJA_BROWSER_TESTS": "1"})
