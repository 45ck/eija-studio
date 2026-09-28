"""Negative controls for scripts/validate_diagram_syntax.py: a validator that cannot fail proves nothing.

The real-browser and PlantUML checks are marked `browser`: they need Chrome or a jar, take ~35 s and are
run by the release session `diagrams_syntax` (EIJA_BROWSER_TESTS=1), not by the fast or full tier. Where
they do not run they are reported as skipped with a NOT_RUN reason, never as passed. In the release session a
missing prerequisite fails the test unless EIJA_ALLOW_NOT_RUN=1.
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from typing import ClassVar

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import validate_diagram_syntax as validator  # noqa: E402

browser = pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1",
                             reason="NOT_RUN: real-browser check; run by the release session diagrams_syntax (EIJA_BROWSER_TESTS=1)")


def not_run(reason: str) -> None:
    """A missing prerequisite: skip on request (dev machine), otherwise fail so a release run cannot look green."""
    if os.environ.get("EIJA_ALLOW_NOT_RUN") == "1":
        pytest.skip("NOT_RUN: " + reason)
    pytest.fail("NOT_RUN: " + reason + " (set EIJA_ALLOW_NOT_RUN=1 to accept on a dev machine)")


@pytest.mark.browser
@browser
def test_mermaid_validator_rejects_garbage_and_accepts_generated_text():
    if importlib.util.find_spec("playwright") is None:
        not_run("playwright is not installed")
    bad = validator.check_mermaid({"garbage": "this is not a diagram", "broken": "flowchart LR\n A --> \n"})
    if bad["status"] == "NOT_RUN":
        not_run(bad["reason"])
    assert bad["status"] == "FAIL" and set(bad["failures"]) == {"garbage", "broken"}
    good = validator.corpus()["mermaid"]
    report = validator.check_mermaid(good)
    assert report["status"] == "PASS" and report["checked"] == len(good), report["failures"]


def test_dot_validator_rejects_broken_dot_and_accepts_generated_text():
    if importlib.util.find_spec("pydot") is None:
        pytest.skip("NOT_RUN: pydot not installed")
    assert validator.check_dot({"broken": "digraph { a -> }"})["status"] == "FAIL"
    good = validator.corpus()["dot"]
    assert validator.check_dot(good)["status"] == "PASS"


@pytest.mark.browser
@browser
def test_plantuml_validator_rejects_garbage_and_catches_label_evaluation():
    jar = os.environ.get("EIJA_PLANTUML_JAR")
    if not jar:
        not_run("EIJA_PLANTUML_JAR is not set")
    text = "@startuml\nstate \"%getenv(PLANTUML_SECRETVAR)\" as a\nstate b\na --> b\n@enduml\n"
    unescaped = validator.check_plantuml({"hostile/raw": text}, jar)
    if unescaped["status"] == "NOT_RUN":
        not_run(unescaped["reason"])
    assert unescaped["status"] == "FAIL" and "evaluated" in unescaped["failures"]["hostile/raw"]  # the control can fail
    assert validator.check_plantuml({"garbage": "@startuml\nthis is ( not uml\n@enduml\n"}, jar)["status"] == "FAIL"
    good = validator.corpus()["plantuml"]
    report = validator.check_plantuml(good, jar)
    assert report["status"] == "PASS" and report["checked"] == len(good), report["failures"]


def test_missing_prerequisites_are_not_run_never_pass(monkeypatch):
    monkeypatch.setattr(validator, "launch_chrome", lambda playwright: None)
    if importlib.util.find_spec("playwright") is not None:
        assert validator.check_mermaid({"x": "graph LR"})["status"] == "NOT_RUN"
    assert validator.check_plantuml({"x": "@startuml\n@enduml"}, "no-such.jar")["status"] == "NOT_RUN"


def test_exit_code_makes_not_run_visible(monkeypatch, capsys):
    """NOT_RUN must not be a silent green: exit 3 by default, 0 only with the explicit opt-out."""
    monkeypatch.setattr(validator, "check_mermaid", lambda texts: {"status": "NOT_RUN", "reason": "test"})
    monkeypatch.setattr(validator, "check_plantuml", lambda texts, jar: {"status": "PASS"})
    monkeypatch.setattr(validator, "check_dot", lambda texts: {"status": "PASS"})
    monkeypatch.setattr(sys, "argv", ["validate"])
    assert validator.main() == 3
    monkeypatch.setattr(sys, "argv", ["validate", "--allow-not-run"])
    assert validator.main() == 0
    monkeypatch.setattr(validator, "check_dot", lambda texts: {"status": "FAIL"})
    assert validator.main() == 1  # a real failure is never allowed


class FakeSession:
    posargs: ClassVar[list[str]] = []

    def __init__(self):
        self.calls = []

    def run(self, *args, **kwargs):
        self.calls.append((args, kwargs))


def test_release_sessions_fail_on_not_run_unless_opted_out(monkeypatch):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "quality" / "sessions"))
    import visual  # noqa: PLC0415 - quality/sessions is not a package; put on sys.path only for this test
    for opted_out in (False, True):
        (monkeypatch.setenv if opted_out else monkeypatch.delenv)(*(("EIJA_ALLOW_NOT_RUN", "1") if opted_out else ("EIJA_ALLOW_NOT_RUN", False)))
        shots, syntax = FakeSession(), FakeSession()
        visual.visual_screenshots.func(shots)
        visual.diagrams_syntax.func(syntax)
        assert shots.calls[0][1]["success_codes"] == ([0, 3] if opted_out else [0])  # exit 3 (NOT_RUN) is a failure by default
        assert ("--allow-not-run" in syntax.calls[-1][0]) is opted_out
