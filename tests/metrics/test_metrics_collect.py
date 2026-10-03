import platform
import subprocess
from types import SimpleNamespace

import pytest

from quality.metrics import collect as collector
from quality.metrics import common
from quality.metrics.__main__ import cmd_drift
from quality.metrics.common import platform_info


def _perf_section(p95):
    endpoints = [{"endpoint": "GET /x", "kind": "read", "p95_ms": p95}]
    return {"status": "MEASURED", "transports": {"testclient": {"status": "MEASURED", "endpoints": endpoints}},
            "verify_scaling": {"r2": 0.99, "alt_quadratic_r2": 0.5}}


@pytest.fixture
def fake_measurements(monkeypatch):
    """Timing measurement replaced by a scripted sequence of p95 values; structural sections by an empty stub."""
    calls = []

    def script(*p95s):
        def measure(sections, profile, real_server):
            calls.append(profile)
            sections["performance"] = _perf_section(p95s[min(len(calls), len(p95s)) - 1])
        monkeypatch.setattr(collector, "_measure_timing", measure)
        return calls

    monkeypatch.setattr(collector, "structural_sections", lambda **_: {"lane_reports": {"status": "NOT_RUN", "reason": "stub"}})
    return script


def _timing_status(doc, budget_id):
    return next(r["status"] for r in doc["budgets"] if r["id"] == budget_id)


def test_timing_is_measured_once_by_default_and_a_failure_stays_a_failure(fake_measurements):
    calls = fake_measurements(900.0, 10.0)
    doc = collector.collect("quick")
    assert len(calls) == 1 and _timing_status(doc, "PERF-01") == "FAIL"
    assert doc["meta"]["timing_runs"] == [{"run": 1, "failed_timing_budgets": ["PERF-01"]}]


def test_a_retry_is_recorded_so_a_later_pass_is_never_presented_as_a_first_time_pass(fake_measurements):
    calls = fake_measurements(900.0, 10.0)
    doc = collector.collect("quick", timing_retries=1)
    assert len(calls) == 2 and _timing_status(doc, "PERF-01") == "PASS"
    assert [r["failed_timing_budgets"] for r in doc["meta"]["timing_runs"]] == [["PERF-01"], []]
    assert "timing_runs" in doc["meta"]["timing_policy"]


def test_retries_are_only_spent_on_failures_and_are_bounded(fake_measurements):
    calls = fake_measurements(10.0)
    collector.collect("quick", timing_retries=3)
    assert len(calls) == 1  # nothing failed: no re-measurement
    calls.clear()
    calls = fake_measurements(900.0)
    doc = collector.collect("quick", timing_retries=2)
    assert len(calls) == 3 and _timing_status(doc, "PERF-01") == "FAIL"  # a persistent failure is reported, not hidden


def test_drift_can_require_the_snapshot_to_match_the_source_tree(monkeypatch, capsys):
    monkeypatch.setattr(collector, "stale_sections", lambda doc: ["martin"])
    assert cmd_drift(SimpleNamespace(freshness="note")) == 0
    assert "STALE" in capsys.readouterr().out  # a warning, never silent
    assert cmd_drift(SimpleNamespace(freshness="require")) == 1
    monkeypatch.setattr(collector, "stale_sections", lambda doc: [])
    assert cmd_drift(SimpleNamespace(freshness="require")) == 0


def test_stale_sections_notices_a_changed_structure(monkeypatch):
    doc = {"sections": {"martin": {"layers": 1}, "complexity": {"functions": 2}}}
    monkeypatch.setattr(collector, "structural_sections", lambda **_: {"martin": {"layers": 1}, "complexity": {"functions": 3}})
    assert collector.stale_sections(doc) == ["complexity"]


def test_platform_label_does_not_go_through_the_wmi_backed_platform_calls(monkeypatch):
    """Regression: platform.system()/release()/machine() emitted a fatal-exception traceback dump on Windows."""
    def boom():
        raise AssertionError("platform WMI-backed call used")
    for name in ("system", "release", "machine", "uname"):
        monkeypatch.setattr(platform, name, boom)
    info = platform_info()
    assert info["python"] and info["system"] and info["label"].endswith(info["python"])


def test_git_state_reports_the_first_dirty_path_intact(monkeypatch, tmp_path):
    """Regression: strip() on the whole porcelain output ate the leading space of the first line, so the first
    dirty path lost its first character ('docs/x' became 'ocs/x')."""
    def git(*args):
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", *args],  # noqa: S603, S607
                       cwd=tmp_path, check=True, capture_output=True)

    git("init", "-q")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "x.txt").write_text("one", encoding="utf-8")
    git("add", ".")
    git("commit", "-q", "-m", "init")
    (tmp_path / "docs" / "x.txt").write_text("two", encoding="utf-8")  # a tracked modification: " M docs/x.txt"
    monkeypatch.setattr(common, "ROOT", tmp_path)
    state = common.git_state()
    assert state["dirty"] is True and state["dirty_paths"] == ["docs/x.txt"]
