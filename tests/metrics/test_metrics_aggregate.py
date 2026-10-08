import hashlib
import json
from pathlib import Path

import pytest

from quality.metrics import aggregate, budgets
from quality.metrics.common import MEASURED, NOT_RUN


def write(path, doc):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(doc if isinstance(doc, str) else json.dumps(doc), encoding="utf-8")


def group(result, name):
    return next(g for g in result["groups"] if g["group"] == name)


def collect(root):
    """aggregate.collect with `rel` pointed at the fixture directory (it lives outside the repo)."""
    return aggregate.collect(root)


def test_missing_reports_are_not_run_never_pass(tmp_path):
    result = collect(tmp_path)
    assert result["summary"]["groups_not_run"] == 4
    assert all(g["status"] == NOT_RUN and g["reports"] == [] for g in result["groups"])


def test_status_is_copied_not_inferred_and_unknown_never_becomes_pass(tmp_path, monkeypatch):
    monkeypatch.setattr(aggregate, "rel", lambda p: p.relative_to(tmp_path).as_posix())
    write(tmp_path / "formal" / "tla.json", {"status": "PASS", "technique": "tlc", "distinct_states": 1200, "duration_s": 2.0})
    write(tmp_path / "formal" / "z3.json", {"result": "sat"})  # no status field
    write(tmp_path / "hci" / "a11y.json", "{not json")
    result = collect(tmp_path)
    formal = group(result, "formal")
    by_file = {r["file"].rsplit("/", 1)[-1]: r for r in formal["reports"]}
    assert by_file["tla.json"]["status"] == "PASS" and by_file["z3.json"]["status"] == "UNKNOWN"
    assert formal["status"] == "UNKNOWN"  # the weakest report decides; unknown never rounds up to PASS
    assert group(result, "hci")["reports"][0]["status"] == "UNREADABLE"
    assert group(result, "mutation")["status"] == NOT_RUN


def test_a_single_fail_dominates_and_trips_the_lane_budget(tmp_path, monkeypatch):
    monkeypatch.setattr(aggregate, "rel", lambda p: p.relative_to(tmp_path).as_posix())
    write(tmp_path / "mutation" / "summary.json", {"status": "FAIL", "summary": {"mutation_score": 0.4, "mutants": 10, "killed": 4}})
    write(tmp_path / "formal" / "bend.json", {"status": "PASS"})
    result = collect(tmp_path)
    assert group(result, "mutation")["reports"][0]["values"] == {"mutation_score": 0.4, "mutants": 10, "killed": 4}
    doc = {"sections": {"lane_reports": result}}
    assert next(r for r in budgets.evaluate(doc) if r["id"] == "LANE-01")["status"] == "FAIL"


def test_yield_rows_only_from_reports_with_state_counts(tmp_path, monkeypatch):
    monkeypatch.setattr(aggregate, "rel", lambda p: p.relative_to(tmp_path).as_posix())
    write(tmp_path / "formal" / "tla.json", {"status": "PASS", "technique": "tlc", "summary": {"states": 2000, "counterexamples": 0, "seconds": 4}})
    write(tmp_path / "formal" / "z3.json", {"status": "PASS", "checks": 12})
    rows = aggregate.yield_rows(collect(tmp_path))
    assert [r["technique"] for r in rows] == ["tlc"]
    assert rows[0]["states_explored"] == 2000 and rows[0]["states_per_s"] == 500 and rows[0]["findings"] == 0


def test_lane_budget_is_not_run_when_no_lane_reported():
    doc = {"sections": {"lane_reports": collect(Path("does-not-exist"))}}
    assert next(r for r in budgets.evaluate(doc) if r["id"] == "LANE-01")["status"] == NOT_RUN
    assert doc["sections"]["lane_reports"]["status"] == MEASURED


def test_lane_budget_does_not_pass_when_every_present_report_is_unreadable_or_unknown(tmp_path, monkeypatch):
    """Regression: LANE-01 used to PASS on corrupt reports or a misspelled status because only FAIL counted."""
    monkeypatch.setattr(aggregate, "rel", lambda p: p.relative_to(tmp_path).as_posix())
    write(tmp_path / "formal" / "a.json", "{not json")
    write(tmp_path / "mutation" / "summary.json", {"status": "passed"})  # not in the PASS/FAIL/NOT_RUN vocabulary
    result = collect(tmp_path)
    assert {g["status"] for g in result["groups"] if g["status"] != NOT_RUN} == {"UNKNOWN"}
    row = next(r for r in budgets.evaluate({"sections": {"lane_reports": result}}) if r["id"] == "LANE-01")
    assert row["status"] == "FAIL" and row["actual"] == 2


def test_lane_budget_passes_only_on_a_definite_pass(tmp_path, monkeypatch):
    monkeypatch.setattr(aggregate, "rel", lambda p: p.relative_to(tmp_path).as_posix())
    write(tmp_path / "formal" / "a.json", {"status": "PASS"})
    doc = {"sections": {"lane_reports": collect(tmp_path)}}
    assert next(r for r in budgets.evaluate(doc) if r["id"] == "LANE-01")["status"] == "PASS"


def test_verdict_and_string_result_are_read_verbatim_but_only_from_the_lane_itself(tmp_path, monkeypatch):
    """The formal-report lanes write `verdict`, the TLA+ lane a string `result`; a nested `result` object and a misspelled verdict stay UNKNOWN."""
    monkeypatch.setattr(aggregate, "rel", lambda p: p.relative_to(tmp_path).as_posix())
    write(tmp_path / "formal" / "smt.json", {"verdict": "PASS"})
    write(tmp_path / "formal" / "tla.json", {"result": "PASS"})
    write(tmp_path / "formal" / "both.json", {"status": "FAIL", "verdict": "PASS"})  # `status` wins: the first field present decides
    write(tmp_path / "formal" / "nested.json", {"result": {"verdict": "PASS"}})
    write(tmp_path / "formal" / "typo.json", {"verdict": "PASSED"})
    by_file = {r["file"].rsplit("/", 1)[-1]: r["status"] for r in group(collect(tmp_path), "formal")["reports"]}
    assert by_file == {"smt.json": "PASS", "tla.json": "PASS", "both.json": "FAIL", "nested.json": "UNKNOWN", "typo.json": "UNKNOWN"}


def hci_trace():
    def observations(modality):
        return {"modality": modality, "steps": [], "operators": [], "pointer_targets": [],
                "views": {}, "errors": [], "http_failures": [], "responsive": None}
    return {"environment": {}, "pointer_passes": [observations("pointer")],
            "keyboard_pass": observations("keyboard")}


def lane_budget(result):
    return next(row for row in budgets.evaluate({"sections": {"lane_reports": result}}) if row["id"] == "LANE-01")


@pytest.mark.parametrize("status", ["PASS", "FAIL"])
def test_hci_trace_is_hashed_input_and_never_changes_the_lane_verdict(tmp_path, monkeypatch, status):
    monkeypatch.setattr(aggregate, "rel", lambda p: p.relative_to(tmp_path).as_posix())
    trace_path = tmp_path / "hci" / "trace.json"
    trace = hci_trace()
    trace["pointer_passes"][0]["audit_navigation"] = []  # additive observation fields remain raw data
    write(trace_path, trace)
    write(tmp_path / "hci" / "report.json", {"status": status})
    result = collect(tmp_path)
    hci = group(result, "hci")
    assert hci["status"] == lane_budget(result)["status"] == status
    assert [report["file"] for report in hci["reports"]] == ["hci/report.json"]
    assert hci["inputs"] == [{"file": "hci/trace.json", "sha256": hashlib.sha256(trace_path.read_bytes()).hexdigest(),
                              "kind": "hci_raw_trace", "reason": "Raw HCI observations; the lane verdict belongs to report.json"}]
    assert aggregate.yield_rows(result) == []


def test_hci_trace_without_a_verdict_report_is_not_run(tmp_path, monkeypatch):
    monkeypatch.setattr(aggregate, "rel", lambda p: p.relative_to(tmp_path).as_posix())
    write(tmp_path / "hci" / "trace.json", hci_trace())
    result = collect(tmp_path)
    hci = group(result, "hci")
    assert hci["status"] == lane_budget(result)["status"] == NOT_RUN
    assert hci["reports"] == [] and len(hci["inputs"]) == 1
    assert "no lane verdict report" in hci["reason"]


@pytest.mark.parametrize("report", [{"status": "passed"}, {"status": None}, {"unknown": True}, "{not json"])
def test_raw_trace_cannot_hide_a_malformed_or_unknown_verdict_report(tmp_path, monkeypatch, report):
    monkeypatch.setattr(aggregate, "rel", lambda p: p.relative_to(tmp_path).as_posix())
    write(tmp_path / "hci" / "trace.json", hci_trace())
    write(tmp_path / "hci" / "report.json", report)
    result = collect(tmp_path)
    assert group(result, "hci")["status"] == "UNKNOWN"
    assert lane_budget(result)["status"] == "FAIL"
    expected = "UNREADABLE" if isinstance(report, str) else "UNKNOWN"
    assert group(result, "hci")["reports"][0]["status"] == expected


@pytest.mark.parametrize("key", ["status", "verdict", "result"])
@pytest.mark.parametrize("value", ["FAIL", "passed", None, {"status": "PASS"}])
def test_trace_with_any_verdict_field_remains_a_report(tmp_path, monkeypatch, key, value):
    monkeypatch.setattr(aggregate, "rel", lambda p: p.relative_to(tmp_path).as_posix())
    trace = {**hci_trace(), key: value}
    write(tmp_path / "hci" / "trace.json", trace)
    write(tmp_path / "hci" / "report.json", {"status": "PASS"})
    result = collect(tmp_path)
    hci = group(result, "hci")
    assert "inputs" not in hci and len(hci["reports"]) == 2
    assert hci["status"] == ("FAIL" if value == "FAIL" else "UNKNOWN")
    assert lane_budget(result)["status"] == "FAIL"


@pytest.mark.parametrize("path", ["hci/other.json", "formal/trace.json", "testing/trace.json"])
def test_trace_shape_at_an_unknown_path_remains_an_unknown_report(tmp_path, monkeypatch, path):
    monkeypatch.setattr(aggregate, "rel", lambda p: p.relative_to(tmp_path).as_posix())
    write(tmp_path / "hci" / "report.json", {"status": "PASS"})
    write(tmp_path / path, hci_trace())
    result = collect(tmp_path)
    assert group(result, path.split("/")[0])["status"] == "UNKNOWN"
    assert lane_budget(result)["status"] == "FAIL"


@pytest.mark.parametrize("change", ["invalid_json", "missing_key", "extra_key", "environment", "empty_passes",
                                    "passes_type", "pointer_type", "pointer_modality", "keyboard_type",
                                    "keyboard_modality", "steps_type", "views_type"])
def test_malformed_trace_shape_is_not_exempted_from_verdict_handling(tmp_path, monkeypatch, change):
    monkeypatch.setattr(aggregate, "rel", lambda p: p.relative_to(tmp_path).as_posix())
    trace = hci_trace()
    mutations = {
        "missing_key": lambda: trace.pop("environment"),
        "extra_key": lambda: trace.update(extra=True),
        "environment": lambda: trace.update(environment=[]),
        "empty_passes": lambda: trace.update(pointer_passes=[]),
        "passes_type": lambda: trace.update(pointer_passes={}),
        "pointer_type": lambda: trace.update(pointer_passes=[None]),
        "pointer_modality": lambda: trace["pointer_passes"][0].update(modality="keyboard"),
        "keyboard_type": lambda: trace.update(keyboard_pass=None),
        "keyboard_modality": lambda: trace["keyboard_pass"].update(modality="pointer"),
        "steps_type": lambda: trace["pointer_passes"][0].update(steps={}),
        "views_type": lambda: trace["keyboard_pass"].update(views=[]),
    }
    if change == "invalid_json":
        trace = "{not json"
    else:
        mutations[change]()
    write(tmp_path / "hci" / "trace.json", trace)
    write(tmp_path / "hci" / "report.json", {"status": "PASS"})
    result = collect(tmp_path)
    hci = group(result, "hci")
    assert "inputs" not in hci and hci["status"] == "UNKNOWN"
    assert lane_budget(result)["status"] == "FAIL"
