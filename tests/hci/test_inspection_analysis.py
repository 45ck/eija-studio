"""Necessary-state evidence is additive; it cannot make a shorter canonical journey look faster."""
from __future__ import annotations

from argparse import Namespace
from copy import deepcopy

import pytest

from quality.hci import __main__ as cli
from quality.hci import analysis, report
from quality.hci.inspection import required_states
from tests.hci import hci_synthetic as syn


def inspection():
    view = syn.view(
        [syn.control("#far", 0, 100, 16, 16), syn.control("#neighbour", 20, 100, 16, 16)],
        violations=[{"id": "aria-required-attr", "impact": "critical", "help": "required ARIA", "help_url": "u", "tags": ["wcag2a"],
                     "nodes": [{"target": "#far", "html": "<button>", "summary": "s"}]}],
        chunks=(20, 22),
    )
    states = required_states()
    views = {"inspection/" + key: syn.view([]) for key in states}
    views["inspection/" + states[0]] = view
    rows = [{"id": key, "status": "PASS", "view": "inspection/" + key,
             "screenshot": {"path": "inspection/" + key + ".png", "sha256": "a" * 64},
             "subject": {"case_id": "synthetic", "revision": 3}} for key in states]
    for row in rows:
        views[row["view"]].update({key: deepcopy(row[key]) for key in ("subject", "screenshot")})
    return {
        "schema": "eija.hci.inspection.v1",
        "required_states": states,
        "planned_states": [{"id": "provider-failure", "reason": "Fault matrix is a later tranche"}],
        "states": rows,
        "views": views,
        "errors": [], "http_failures": [],
        # Huge setup costs are deliberate controls: none belong in the canonical journey models.
        "steps": [syn.step("inspection-setup", 999999.0, decision=(999, 999))],
        "operators": [{"step": "inspection-setup", "op": "M", "note": "setup"}] * 99,
        "pointer_targets": [syn.target("inspection-setup", "setup", [0, 0], [9999, 9999], 4, 4)],
    }


def inspected_raw():
    raw = syn.raw()
    raw["inspection_pass"] = inspection()
    return raw


def test_actual_inspection_views_contribute_to_density_and_accessibility():
    metrics = analysis.analyse(inspected_raw())
    assert metrics["working_memory"]["summary"]["max_chunks_viewport"] == 42
    assert metrics["working_memory"]["summary"]["views"] == 2 + len(required_states())
    assert metrics["wcag"]["summary"]["critical"] == 1
    assert metrics["wcag"]["summary"]["target_size_failures"] == 4
    assert "inspection/workspace-work-views-1440" in metrics["wcag"]["views_audited"]
    assert metrics["inspection"]["completed"] is True
    assert metrics["inspection"]["summary"] == dict.fromkeys(("required", "observed", "passed"), len(required_states()))
    assert "inspection views use the actual viewport after native activation" in metrics["working_memory"]["definition"]


def test_inspection_never_changes_canonical_models_targets_or_timing():
    legacy = analysis.analyse(syn.raw())
    raw = inspected_raw()
    untouched = deepcopy(raw)
    metrics = analysis.analyse(raw)
    for key in ("fitts", "hick_hyman", "klm", "keyboard", "measured", "journey"):
        assert metrics[key] == legacy[key], key
    assert next(t for t in metrics["fitts"]["targets"] if t["selector"] == "#far")["wcag_2_5_8"] == "not-audited"
    assert raw == untouched  # No mutation of the canonical trace or inspection trace.


@pytest.mark.parametrize("defect", ["missing", "duplicate", "view-missing", "FAIL", "NOT_RUN"])
def test_required_state_defects_fail_the_lane_without_a_budget_regression(defect):
    raw = inspected_raw()
    data = raw["inspection_pass"]
    if defect == "missing":
        data["states"] = []
    elif defect == "duplicate":
        data["states"].append(deepcopy(data["states"][0]))
    elif defect == "view-missing":
        data["views"] = {}
    else:
        data["states"][0].update(status=defect, reason="native control unavailable")
    rep = report.build_report(raw, budget_defs=[])
    assert rep["budgets"] == []
    assert rep["inspection"]["status"] == "FAIL"
    assert rep["inspection"]["completed"] is False
    assert rep["inspection"]["issues"]
    assert cli.lane_status(rep) == "FAIL"


def test_failed_state_still_counts_its_actual_captured_view():
    raw = inspected_raw()
    raw["inspection_pass"]["states"][0].update(status="FAIL", reason="wrong subject")
    metrics = analysis.analyse(raw)
    assert metrics["working_memory"]["summary"]["max_chunks_viewport"] == 42
    assert metrics["wcag"]["summary"]["critical"] == 1
    assert metrics["inspection"]["status"] == "FAIL"


@pytest.mark.parametrize("target", ["state", "view"])
@pytest.mark.parametrize("field", ["subject", "screenshot"])
def test_missing_evidence_binding_fails_coverage_but_keeps_actual_view(target, field):
    raw = inspected_raw()
    state = raw["inspection_pass"]["states"][0]
    view = raw["inspection_pass"]["views"][state["view"]]
    (state if target == "state" else view).pop(field)
    rep = report.build_report(raw, budget_defs=[])
    assert cli.lane_status(rep) == "FAIL"
    assert rep["inspection"]["summary"]["passed"] == len(required_states()) - 1
    assert any(field in issue for issue in rep["inspection"]["issues"])
    assert rep["working_memory"]["summary"]["max_chunks_viewport"] == 42
    assert rep["wcag"]["summary"]["critical"] == 1
    assert "Coverage **FAIL**" in report.render_markdown(rep)


@pytest.mark.parametrize("field,replacement", [
    ("subject", {"case_id": "another-case", "revision": 3}),
    ("screenshot", {"path": "inspection/another-state.png", "sha256": "b" * 64}),
])
def test_state_cannot_claim_another_subject_or_screenshot(field, replacement):
    raw = inspected_raw()
    raw["inspection_pass"]["states"][0][field] = replacement
    coverage = analysis.analyse(raw)["inspection"]
    assert coverage["completed"] is False
    assert any(field in issue for issue in coverage["issues"])


@pytest.mark.parametrize("field,key,value", [
    ("subject", "case_id", "  "), ("subject", "revision", "3"), ("subject", "revision", True),
    ("screenshot", "path", "inspection/../other.png"), ("screenshot", "path", "C:/other.png"),
    ("screenshot", "path", "inspection\\other.png"), ("screenshot", "path", "inspection/other.svg"),
    ("screenshot", "sha256", "a" * 63), ("screenshot", "sha256", "z" * 64),
    ("screenshot", "sha256", None),
])
def test_matching_but_invalid_evidence_cannot_pass(field, key, value):
    raw = inspected_raw()
    state = raw["inspection_pass"]["states"][0]
    state[field][key] = value
    raw["inspection_pass"]["views"][state["view"]][field][key] = value
    rep = report.build_report(raw, budget_defs=[])
    assert cli.lane_status(rep) == "FAIL"
    assert "Coverage **FAIL**" in report.render_markdown(rep)


@pytest.mark.parametrize("view_key", ["one", "unprefixed-view", "inspection/existing-canonical"])
def test_invalid_view_keys_preserve_measurements_without_replacing_canonical_evidence(view_key):
    raw = inspected_raw()
    if view_key.startswith("inspection/"):
        raw["pointer_passes"][0]["views"][view_key] = syn.view([])
    owner_raw = deepcopy(raw)
    owner_raw.pop("inspection_pass")
    owner_metrics = analysis.analyse(owner_raw)
    data = raw["inspection_pass"]
    data["views"][view_key] = data["views"].pop("inspection/workspace-work-views-1440")
    data["states"][0]["view"] = view_key
    untouched = deepcopy(raw)
    metrics = analysis.analyse(raw)
    assert metrics["inspection"]["status"] == "FAIL"
    assert metrics["inspection"]["summary"]["passed"] == len(required_states()) - 1
    assert metrics["wcag"]["summary"]["critical"] == 1
    assert metrics["working_memory"]["summary"]["max_chunks_viewport"] == 42
    rows = {row["view"]: row for row in metrics["working_memory"]["views"]}
    assert rows["one"]["chunks_viewport"] == 7
    alias, = metrics["inspection"]["audit_view_aliases"]
    assert metrics["inspection"]["audit_view_aliases"][alias] == view_key
    assert rows[alias]["chunks_viewport"] == 42
    assert alias in metrics["wcag"]["views_audited"]
    for key in ("fitts", "hick_hyman", "klm", "keyboard", "measured", "journey"):
        assert metrics[key] == owner_metrics[key], key
    assert raw == untouched


def test_invalid_view_alias_cannot_overwrite_an_existing_captured_view():
    raw = inspected_raw()
    data = raw["inspection_pass"]
    reserved = "inspection/invalid-key-0001"
    original = data["views"].pop("inspection/workspace-work-views-1440")
    data["views"]["one"] = original
    data["states"][0]["view"] = "one"
    data["views"][reserved] = syn.view([], chunks=(1, 8))
    metrics = analysis.analyse(raw)
    rows = {row["view"]: row for row in metrics["working_memory"]["views"]}
    assert rows[reserved]["chunks_viewport"] == 9
    assert rows["inspection/invalid-key-0002"]["chunks_viewport"] == 42
    assert metrics["inspection"]["audit_view_aliases"] == {"inspection/invalid-key-0002": "one"}
    assert metrics["inspection"]["status"] == "FAIL"
    assert metrics["wcag"]["summary"]["critical"] == 1


def test_reusing_one_view_for_two_states_cannot_claim_both_were_captured():
    raw = inspected_raw()
    data = raw["inspection_pass"]
    data["required_states"].append("inspector-open")
    data["states"].append({**data["states"][0], "id": "inspector-open"})
    coverage = analysis.analyse(raw)["inspection"]
    assert coverage["status"] == "FAIL"
    assert any("shared by multiple states" in issue for issue in coverage["issues"])


def test_empty_or_duplicate_declarations_cannot_pass():
    for required in ([], required_states()[1:], [*required_states(), required_states()[0]]):
        raw = inspected_raw()
        raw["inspection_pass"]["required_states"] = required
        assert analysis.analyse(raw)["inspection"]["completed"] is False


def test_inspection_runtime_errors_join_existing_hygiene_metrics():
    raw = inspected_raw()
    raw["inspection_pass"]["errors"] = ["pageerror: inspection failed", "console.error: warning"]
    raw["inspection_pass"]["http_failures"] = [{"status": 500, "method": "GET", "path": "/api/state", "step": "details"}]
    hygiene = analysis.analyse(raw)["runtime_errors"]
    assert hygiene["javascript_exceptions"] == ["pageerror: inspection failed"]
    assert hygiene["javascript_exception_count"] == 1
    assert hygiene["http_error_responses"] == raw["inspection_pass"]["http_failures"]


def test_lifecycle_failure_cannot_pass_even_if_all_states_were_captured():
    raw = inspected_raw()
    raw["inspection_pass"]["errors"] = ["inspection-1440: context cleanup failed"]
    rep = report.build_report(raw, budget_defs=[])
    assert rep["inspection"]["summary"]["passed"] == len(required_states())
    assert rep["inspection"]["issues"] == ["inspection-1440: context cleanup failed"]
    assert cli.lane_status(rep) == "FAIL"


def test_expected_console_errors_do_not_imply_missing_inspection_coverage():
    raw = inspected_raw()
    raw["inspection_pass"]["errors"] = ["console.error: expected refusal"]
    assert analysis.analyse(raw)["inspection"]["completed"] is True


def test_legacy_trace_has_no_new_report_section_and_retains_budget_only_verdict():
    rep = report.build_report(syn.raw(), budget_defs=[])
    assert "inspection" not in rep
    assert "Necessary-state inspection" not in report.render_markdown(rep)
    assert cli.lane_status(rep) == "PASS"


def test_report_exposes_coverage_screenshot_and_planned_states():
    rep = report.build_report(inspected_raw(), budget_defs=[])
    markdown = report.render_markdown(rep)
    assert "Coverage **PASS**: 18/18 required states" in markdown
    assert "inspection/workspace-work-views-1440.png" in markdown
    assert "provider-failure | NOT_RUN | Fault matrix is a later tranche" in markdown
    assert rep["inspection"]["states"][0]["subject"] == {"case_id": "synthetic", "revision": 3}
    assert cli.lane_status(rep) == "PASS"


def test_cli_uses_output_directory_for_inspection_artifacts(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(cli.journey, "prerequisites", lambda: (True, "synthetic prerequisite"))
    monkeypatch.setattr(cli.journey, "collect", lambda **kwargs: calls.append(kwargs) or {})
    args = Namespace(out=str(tmp_path), repeats=2, headed=False, identity="harness")
    assert cli._collect(args) == ({}, 0)
    assert calls == [{"repeats": 2, "headless": True, "identity": "harness", "inspection_out": tmp_path / "inspection"}]


def test_cli_returns_failure_for_missing_inspection_even_when_budgets_pass(monkeypatch, tmp_path, capsys):
    raw = inspected_raw()
    raw["inspection_pass"]["states"] = []
    rep = report.build_report(raw, budget_defs=[])
    monkeypatch.setattr(cli, "_collect", lambda _: (raw, 0))
    monkeypatch.setattr(cli.report, "build_report", lambda *args, **kwargs: rep)
    monkeypatch.setattr(cli, "_write_outputs", lambda *args: None)
    args = Namespace(out=str(tmp_path), date=None, publish_docs=False)
    assert cli.cmd_run(args) == 1
    assert "FAIL inspection: Required state not observed: workspace-work-views-1440" in capsys.readouterr().out
