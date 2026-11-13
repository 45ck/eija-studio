"""A skipped nox session is NOT_RUN, never PASS: the hosted workflow reads the report, not only nox's exit code."""
from __future__ import annotations

import json
from pathlib import Path

from quality.tools import nox_report


def _report(tmp_path, *sessions):
    path = tmp_path / "nox.json"
    path.write_text(json.dumps({"result": 1, "sessions": [
        {"name": name, "result": result, "reason": reason} for name, result, reason in sessions]}), encoding="utf-8")
    return path


def test_every_session_ran_and_passed_is_success(tmp_path, capsys):
    path = _report(tmp_path, ("lint", "success", None), ("tests", "success", None))
    assert nox_report.main([str(path), "--fail-on-skip"]) == 0
    assert "2 passed, 0 failed, 0 NOT_RUN" in capsys.readouterr().out


def test_a_skipped_session_fails_the_strict_tier_and_is_named(tmp_path, capsys):
    path = _report(tmp_path, ("lint", "success", None), ("okf_structure", "skipped", "NOT_RUN: install the okf extra"))
    assert nox_report.main([str(path), "--fail-on-skip"]) == 1
    assert "NOT_RUN okf_structure: NOT_RUN: install the okf extra" in capsys.readouterr().out


def test_without_the_strict_flag_a_skip_is_listed_but_not_a_failure(tmp_path, capsys):
    path = _report(tmp_path, ("lint", "success", None), ("formal_bend", "skipped", "no Docker"))
    assert nox_report.main([str(path)]) == 0
    assert "1 NOT_RUN" in capsys.readouterr().out


def test_a_failed_session_always_fails(tmp_path):
    assert nox_report.main([str(_report(tmp_path, ("lint", "failed", None)))]) == 1


def test_a_missing_or_empty_report_is_not_a_pass(tmp_path):
    assert nox_report.main([str(tmp_path / "absent.json")]) == 1
    assert nox_report.main([str(_report(tmp_path))]) == 1


def test_the_summary_goes_to_the_hosted_job_summary(tmp_path, monkeypatch):
    summary = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
    nox_report.main([str(_report(tmp_path, ("mutation_quick", "skipped", "cosmic-ray missing")))])
    assert "NOT_RUN mutation_quick: cosmic-ray missing" in summary.read_text(encoding="utf-8")


def test_the_hosted_workflow_reads_the_report_and_installs_the_extras_the_gates_need():
    workflow = (Path(__file__).resolve().parents[2] / ".github" / "workflows" / "quality.yml").read_text(encoding="utf-8")
    assert "nox -t fast --report" in workflow and "quality.tools.nox_report reports/nox-fast.json --fail-on-skip" in workflow
    assert "nox -t full --report" in workflow and "quality.tools.nox_report reports/nox-full.json" in workflow
    installs = [line.split("'.[", 1)[1].split("]'", 1)[0].split(",") for line in workflow.splitlines() if "pip install -e '.[" in line]
    assert len(installs) == 2, "the fast and the full job each install the project"
    for extras in installs:
        assert {"dev", "lint", "graph", "graph-formal", "okf", "interop-api", "smt", "mutation"} <= set(extras), extras
