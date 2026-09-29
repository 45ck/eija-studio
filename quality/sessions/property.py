"""Property-based and stateful model-based tests (Hypothesis). ADR-0031.

``property`` runs in the ``full`` tier with the derandomized ``ci`` profile (the same examples on every
machine). ``property_deep`` runs in the ``release`` tier with random seeds and ten times the examples,
saving failures to ``.hypothesis/`` (gitignored). Both write example counts to ``reports/testing/``.
A missing Hypothesis install is reported NOT_RUN, never PASS.
"""
import importlib.util
import json
import sys
from pathlib import Path

import nox

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False
ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports" / "testing"
MISSING = "hypothesis / hypothesis-jsonschema not installed: pip install -e '.[dev,testing]'"


def run_profile(session: nox.Session, profile: str, report: str) -> None:
    missing = [m for m in ("hypothesis", "hypothesis_jsonschema", "jsonschema") if importlib.util.find_spec(m) is None]
    if missing:
        REPORTS.mkdir(parents=True, exist_ok=True)
        (REPORTS / report).write_bytes((json.dumps({"schema": "eija.testing.property.v1", "profile": profile,
            "status": "NOT_RUN", "reason": f"{MISSING} (missing: {', '.join(missing)})"}, indent=2, sort_keys=True) + "\n").encode("utf-8"))
        session.skip(f"NOT_RUN: {MISSING}")
    env = {"EIJA_HYPOTHESIS_PROFILE": profile, "EIJA_PROPERTY_REPORT": f"reports/testing/{report}"}
    session.run(PYTHON, "-m", "pytest", "tests/property", "-q", "-p", "no:cacheprovider", *session.posargs, env=env)


@nox.session(name="property", python=False, tags=["full"])
def property_tests(session: nox.Session) -> None:
    """Hypothesis properties + stateful differential test, ci profile (derandomized, fast)."""
    run_profile(session, "ci", "property.json")


@nox.session(name="property_deep", python=False, tags=["release"])
def property_deep(session: nox.Session) -> None:
    """The same suite with random seeds and 10x examples; failures are saved under .hypothesis/."""
    run_profile(session, "deep", "property-deep.json")
