"""UML interchange lane gate (ADR-0190): committed exports, faithful round trips and two independent parsers.

`interop_roundtrip` is pure Python: the committed files in verification/interop/generated/ match a fresh export, and
every pack's export in every format imports back CLEAN and unchanged.
`interop_mermaid` has Mermaid's own parser (the vendored bundle, in Chromium) read every Mermaid export and agree with
PlayIDE's reading. `interop_plantuml` does the same with PlantUML (the pinned MIT jar, on Java). Each also proves its
negative controls are caught. A missing browser, Java or jar reports NOT_RUN and the session is skipped; it never
passes silently.
"""
import json
import sys
from pathlib import Path

import nox
from nox.command import CommandFailed

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False
REPORTS = Path("reports") / "interop"


@nox.session(python=False, tags=["fast", "full"])
def interop_roundtrip(session: nox.Session) -> None:
    """The committed UML exports are current, and every export reads back as exactly the model it came from."""
    session.run(PYTHON, "-m", "verification.interop.generate", "--check")


def _oracle(session: nox.Session, module: str, name: str) -> None:
    report_path = REPORTS / f"{name}.json"
    report_path.unlink(missing_ok=True)
    try:
        session.run(PYTHON, "-m", f"verification.interop.{module}", "--out", str(report_path), success_codes=[0, 3])
    except CommandFailed:
        session.error(f"interop_{name} FAIL: see {report_path}")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if report.get("status") == "NOT_RUN":
        session.skip(f"NOT_RUN: {report.get('reason')}")
    if report.get("status") != "PASS":
        session.error(f"interop_{name} FAIL: see {report_path}")


@nox.session(python=False, tags=["full", "release"])
def interop_mermaid(session: nox.Session) -> None:
    """Mermaid's own parser reads every Mermaid export as PlayIDE does; its negative controls are caught."""
    _oracle(session, "mermaid_oracle", "mermaid")


@nox.session(python=False, tags=["full", "release"])
def interop_plantuml(session: nox.Session) -> None:
    """PlantUML reads every PlantUML export as PlayIDE does; its negative controls are caught."""
    _oracle(session, "plantuml_oracle", "plantuml")
