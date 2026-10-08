"""App-generation lane gate (ADR-0150): every authored pack builds an app that passes its kernel conformance run."""

import shutil
import sys
from pathlib import Path

import nox

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "appgen"


@nox.session(python=False, tags=["full", "release"])
def appgen(session: nox.Session) -> None:
    """`eija build` for each pack into reports/appgen/; a FAIL (exit 2) or refusal fails the session."""
    shutil.rmtree(OUT, ignore_errors=True)
    for pack in sorted(p.name for p in (ROOT / "packs").iterdir() if (p / "pack.json").is_file()):
        session.run(
            PYTHON,
            "-m",
            "eija_studio",
            "build",
            "--pack",
            str(ROOT / "packs" / pack),
            "--out",
            str(OUT / pack),
        )
