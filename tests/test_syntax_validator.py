"""Negative controls for scripts/validate_diagram_syntax.py: a validator that cannot fail proves nothing.

Skipped (not passed) when Chrome, Playwright or pydot is missing, so a bare machine reports the gap.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import validate_diagram_syntax as validator  # noqa: E402


def test_mermaid_validator_rejects_garbage_and_accepts_generated_text():
    if importlib.util.find_spec("playwright") is None or not any(p.is_file() for p in validator.CHROME):
        pytest.skip("Chrome or Playwright not available")
    good = validator.corpus()["mermaid"]
    assert validator.check_mermaid({"garbage": "this is not a diagram", "broken": "flowchart LR\n A --> \n"})["status"] == "FAIL"
    report = validator.check_mermaid(good)
    assert report["status"] == "PASS" and report["checked"] == len(good), report["failures"]


def test_dot_validator_rejects_broken_dot_and_accepts_generated_text():
    if importlib.util.find_spec("pydot") is None:
        pytest.skip("pydot not installed")
    assert validator.check_dot({"broken": "digraph { a -> }"})["status"] == "FAIL"
    good = validator.corpus()["dot"]
    assert validator.check_dot(good)["status"] == "PASS"


def test_missing_prerequisites_are_not_run_never_pass(monkeypatch):
    monkeypatch.setattr(validator, "CHROME", [Path("does-not-exist.exe")])
    assert validator.check_mermaid({"x": "graph LR"})["status"] == "NOT_RUN"
    assert validator.check_plantuml({"x": "@startuml\n@enduml"}, "no-such.jar")["status"] == "NOT_RUN"
