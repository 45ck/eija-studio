"""Formal lane: Bend 2 machine-checked authority laws (docs/formal/bend.md, ADR-0025).

    nox -s bend_drift          fast: the committed main.bend is the regeneration of the Python model
    nox -s formal_bend_quick   full: the proof, the negative controls and runtime conformance (about a minute)
    nox -s formal_bend         release: the same plus per-law attribution of every control (a few minutes)

The two Docker sessions need Docker Desktop (or a Docker daemon) and, for the first build only, network
access to fetch the pinned Bend and Lean archives. When a prerequisite is missing they report NOT_RUN by
skipping the session: a skipped session is not a pass. The evidence report is written to
``reports/formal/bend.json`` (``kind: bend_proof``). ``nox -s formal_bend -- --snapshot`` also refreshes the
committed platform-named snapshot ``verification/bend/evidence/bend.json`` (maintainers only).
"""
import json
import subprocess
import sys
from pathlib import Path

import nox

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False
ROOT = Path(__file__).resolve().parents[2]
RUNNER = "verification/bend/bend_runner.py"
REPORT = ROOT / "reports" / "formal" / "bend.json"
REPORT_QUICK = ROOT / "reports" / "formal" / "bend-quick.json"
NOT_RUN = 3  # bend_runner exit codes: 0 PASS, 1 FAIL, 3 NOT_RUN


def _run_gate(session: nox.Session, report: Path, *args: str) -> None:
    code = subprocess.run([PYTHON, RUNNER, "--report", str(report), *args, *session.posargs], cwd=ROOT).returncode
    if code == NOT_RUN:
        reason = json.loads(report.read_text(encoding="utf-8")).get("reason", "prerequisite missing")
        session.skip(f"NOT_RUN (not a pass): {reason}")
    if code != 0:
        session.error(f"bend_proof FAIL: see {report.relative_to(ROOT)}")


@nox.session(python=False, tags=["fast", "full"])
def bend_drift(session: nox.Session) -> None:
    """The committed Bend model equals regeneration from the executable Workflow; laws and proofs pair up."""
    session.run(PYTHON, "verification/bend/bend_generate.py", "--check")
    session.run(PYTHON, "-m", "pytest", "-q", "tests/test_formal_bend.py",
                "-k", "deterministic or law_has_a_proof or escape_hatches or docs_name")


@nox.session(python=False, tags=["full"])
def formal_bend_quick(session: nox.Session) -> None:
    """bend PROOF.bend --verdict in the pinned container, negative controls, runtime conformance."""
    _run_gate(session, REPORT_QUICK, "--quick")


@nox.session(python=False, tags=["release"])
def formal_bend(session: nox.Session) -> None:
    """The complete Bend evidence: proof, per-law attribution, negative controls, conformance."""
    _run_gate(session, REPORT)
