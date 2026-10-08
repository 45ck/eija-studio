"""Vocabulary fitness gate (WBS 1.5): no domain pack's vocabulary in generic code (quality/gates/vocabulary.py)."""
import sys

import nox

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False


@nox.session(python=False, tags=["fast", "full"])
def vocabulary(session: nox.Session) -> None:
    """Pack tokens outside packs/, GENERATED files and the justified allowlist fail; so does any Literal naming one."""
    session.run(PYTHON, "-m", "quality.gates.vocabulary")
    session.run(PYTHON, "-m", "pytest", "-q", "tests/tools/test_vocabulary_gate.py", *session.posargs)
