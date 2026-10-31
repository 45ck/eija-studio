"""Vocabulary fitness gate (WBS 1.5): no domain pack's vocabulary in generic code (quality/gates/vocabulary.py)."""
import sys

import nox

from quality.tools.suite import run_lane_tests

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False


@nox.session(python=False, tags=["fast", "full"])
def vocabulary(session: nox.Session) -> None:
    """Pack tokens outside packs/, GENERATED files and the justified allowlist fail; so does any Literal naming one."""
    session.run(PYTHON, "-m", "quality.gates.vocabulary")
    run_lane_tests(session, "tests/tools/test_vocabulary_gate.py")
