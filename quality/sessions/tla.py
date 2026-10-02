"""TLA+ / TLC lane: generated-model drift check and the formal_tla gate.

`tla_drift` is pure Python (seconds). `formal_tla` needs Java 11+ and the pinned tla2tools.jar
(downloaded once into .cache/tla and verified against verification/tla/TOOLS.lock); without them the
session reports NOT_RUN and is skipped. It never passes silently.
"""
import json
import sys
from pathlib import Path
from uuid import uuid4

import nox
from nox.command import CommandFailed

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False
REPORT = Path("reports") / "formal" / "tla.json"


@nox.session(python=False, tags=["fast", "full"])
def tla_drift(session: nox.Session) -> None:
    """The committed TLA+ model modules match the kernel's workflow, actor directory and bounds."""
    session.run(PYTHON, "-m", "verification.tla.generate", "--check")


def _retain_previous(session: nox.Session) -> None:
    if REPORT.exists():
        previous = REPORT.with_name(f"{REPORT.stem}.previous-{uuid4().hex}{REPORT.suffix}")
        REPORT.replace(previous)
        session.log(f"Previous TLA evidence retained: {previous}")


def _run(session: nox.Session, *extra: str) -> None:
    if any(arg.split("=", 1)[0] in {"--out", "--configs"} for arg in session.posargs):
        session.error("formal_tla requires the complete configuration set and its fixed report; use the standalone runner for subsets")
    _retain_previous(session)
    # A crashed child must fail even if an old report said PASS. A zero-exit child
    # must also produce this invocation's report before any verdict is trusted.
    try:
        session.run(PYTHON, "-m", "verification.tla.run", *extra, *session.posargs, "--out", str(REPORT), "--configs", "")
    except CommandFailed as exc:
        _retain_previous(session)
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps({"result": "FAIL", "reason": f"TLA runner execution failed: {exc}",
                                      "reported_by": "formal_tla gate"}) + "\n", encoding="utf-8", newline="\n")
        raise
    try:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        session.error(f"formal_tla FAIL: no readable current report at {REPORT}: {exc}")
    if not isinstance(report, dict) or report.get("result") not in ("PASS", "FAIL", "NOT_RUN"):
        session.error(f"formal_tla FAIL: invalid current report at {REPORT}")
    if report["result"] == "NOT_RUN":
        session.skip(f"NOT_RUN: {report.get('reason')}")
    if report["result"] != "PASS":
        session.error(f"formal_tla FAIL: see {REPORT}")
    session.log(f"formal_tla PASS: {REPORT}")


@nox.session(python=False, tags=["full"])
def formal_tla(session: nox.Session) -> None:
    """TLC model check of Excursion.tla, negative controls, and runtime-vs-spec conformance."""
    _run(session)


@nox.session(python=False, tags=["release"])
def formal_tla_deep(session: nox.Session) -> None:
    """formal_tla plus the candidate model checked with 5 operation ids (about 28k states)."""
    _run(session, "--deep")
