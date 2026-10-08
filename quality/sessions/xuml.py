"""Executable UML lane gate (ADR-0165): the SCXML export of every pack, and the differential against the kernel.

`scxml_drift` is pure Python: the committed charts in verification/scxml/generated/ match a fresh export.
`scxml_differential` runs every app-oracle case on python-statemachine (the `xuml` extra) and on the kernel and fails
on any disagreement. Without the engine it reports NOT_RUN and is skipped; it never passes silently.
"""
import json
import sys
from pathlib import Path

import nox
from nox.command import CommandFailed

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False
REPORT = Path("reports") / "scxml" / "differential.json"


@nox.session(python=False, tags=["fast", "full"])
def scxml_drift(session: nox.Session) -> None:
    """The committed SCXML charts match the packs' models."""
    session.run(PYTHON, "-m", "verification.scxml.generate", "--check")


@nox.session(python=False, tags=["full", "release"])
def scxml_differential(session: nox.Session) -> None:
    """Every oracle case gives the same outcome on an independent SCXML engine as on the kernel."""
    REPORT.unlink(missing_ok=True)
    try:
        session.run(PYTHON, "-m", "verification.scxml.differential", "--out", str(REPORT), success_codes=[0, 3])
    except CommandFailed:
        session.error(f"scxml_differential FAIL: see {REPORT}")
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    if report.get("status") == "NOT_RUN":
        session.skip(f"NOT_RUN: {report.get('reason')}")
    if report.get("status") != "PASS":
        session.error(f"scxml_differential FAIL: see {REPORT}")
