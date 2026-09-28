"""TLA+ / TLC lane: generated-model drift check and the formal_tla gate.

`tla_drift` is pure Python (seconds). `formal_tla` needs Java 11+ and the pinned tla2tools.jar
(downloaded once into .cache/tla and verified against verification/tla/TOOLS.lock); without them the
session reports NOT_RUN and is skipped. It never passes silently.
"""
import json
import sys
from pathlib import Path

import nox

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False
REPORT = Path("reports") / "formal" / "tla.json"


@nox.session(python=False, tags=["fast", "full"])
def tla_drift(session: nox.Session) -> None:
    """The committed TLA+ model modules match the kernel's workflow, actor directory and bounds."""
    session.run(PYTHON, "-m", "verification.tla.generate", "--check")


def _run(session: nox.Session, *extra: str) -> None:
    session.run(PYTHON, "-m", "verification.tla.run", *extra, *session.posargs, success_codes=[0, 1])
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    if report["result"] == "NOT_RUN":
        session.skip(f"NOT_RUN: {report.get('reason')}")
    if report["result"] != "PASS":
        session.error(f"formal_tla FAIL: see {REPORT}")
    print(f"formal_tla PASS: {REPORT}")


@nox.session(python=False, tags=["full"])
def formal_tla(session: nox.Session) -> None:
    """TLC model check of Excursion.tla, negative controls, and runtime-vs-spec conformance."""
    _run(session)


@nox.session(python=False, tags=["release"])
def formal_tla_deep(session: nox.Session) -> None:
    """formal_tla plus the candidate model checked with 5 operation ids (about 28k states)."""
    _run(session, "--deep")
