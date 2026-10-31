"""Run a lane session's own pytest files only when the whole-suite session of the same nox run will not.

`tests` (fast tier) and `coverage` (full tier) run all of tests/ under the default marker selection from
pyproject.toml. Several lane sessions also ran their own files under tests/ with that same selection, so
`nox -t fast` and `nox -t full` ran those files twice (about 75 s of a 4 minute fast tier on a 4-core machine).

A lane session now runs its files itself only when neither suite session is selected in this run, so
`nox -s vocabulary` alone still runs its tests, and a tier runs each file once. Only plain path (and `-k`)
selections under tests/ belong here: a session that adds `-m`, a different environment that changes outcomes,
or files outside tests/ must keep calling pytest itself.

    EIJA_LANE_TESTS=always   run the lane's files even when the suite session runs them too (the old behaviour)
"""

from __future__ import annotations

import os
import sys

import nox

SUITE_SESSIONS = frozenset({"tests", "coverage"})


def suite_selected(session: nox.Session) -> bool:
    """True when `tests` or `coverage` runs (or ran) in this nox invocation.

    Reads nox's manifest, which has no public API for the selected set. If that internal shape changes, the answer
    is False and the lane runs its tests: an unknown state costs time, never coverage.
    """
    try:
        manifest = session._runner.manifest  # nox exposes no public "selected sessions" view
        selected = [*manifest._consumed, *manifest._queue]
        return any(runner.name in SUITE_SESSIONS for runner in selected)
    except AttributeError:
        return False


def run_lane_tests(session: nox.Session, *pytest_args: str, env: dict[str, str] | None = None) -> None:
    """`pytest -q <pytest_args> <posargs>`, unless the suite session of this run covers the same files."""
    # Extra arguments (`nox -t fast -- tests/test_x.py`) also narrow the suite session's collection, so it may no longer
    # cover the lane's files: the lane runs them itself then.
    if os.environ.get("EIJA_LANE_TESTS") != "always" and not session.posargs and suite_selected(session):
        session.log(
            f"{' '.join(pytest_args)}: run by the suite session in this run (EIJA_LANE_TESTS=always runs them here too)"
        )
        return
    session.run(sys.executable, "-m", "pytest", "-q", *pytest_args, *session.posargs, env=env)
