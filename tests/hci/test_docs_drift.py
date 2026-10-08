"""Committed HCI evidence must be reproducible from its own committed trace (no browser)."""
import json
import shutil

import pytest

from quality.hci import analysis, budgets, journey, report


@pytest.fixture
def docs_copy(tmp_path):
    """A scratch copy of the committed evidence, so tamper experiments never touch the repo."""
    paths = {"snapshot_path": tmp_path / "report.snapshot.json", "trace_path": tmp_path / "trace.snapshot.json",
             "report_path": tmp_path / "REPORT.md"}
    for src, dst in ((report.SNAPSHOT, paths["snapshot_path"]), (report.TRACE, paths["trace_path"]), (report.REPORT_MD, paths["report_path"])):
        shutil.copyfile(src, dst)
    return paths


def test_report_md_and_snapshot_are_exactly_derived_from_the_committed_trace():
    ok, message = report.check_docs()
    assert ok, message


def test_snapshot_is_canonical_json_with_lf_endings_and_names_its_platform():
    raw = report.SNAPSHOT.read_bytes()
    assert b"\r" not in raw and raw.endswith(b"\n")
    snapshot = json.loads(raw)
    assert raw.decode("utf-8") == report.dumps(snapshot)
    assert snapshot["schema"] == report.SCHEMA
    assert snapshot["environment"]["platform"] and snapshot["environment"]["chrome"]
    assert snapshot["environment"]["identity_source"] == "pytest-harness"
    assert "\r" not in report.REPORT_MD.read_text(encoding="utf-8")
    trace = report.TRACE.read_bytes()
    assert b"\r" not in trace and trace.decode("utf-8") == report.dump_trace(json.loads(trace))


def test_check_passes_on_an_untouched_copy(docs_copy):
    assert report.check_docs(**docs_copy)[0]


def test_editing_a_law_constant_without_refresh_is_caught(docs_copy, monkeypatch):
    """Regression for the review finding: the fast gate used to be blind to laws.py edits."""
    monkeypatch.setattr(analysis, "FITTS", analysis.laws.FittsModel(b=0.300))
    ok, message = report.check_docs(**docs_copy)
    assert not ok and "DRIFT" in message and "laws" in message


def test_editing_a_budget_limit_without_refresh_is_caught(docs_copy, monkeypatch):
    loosened = [dict(b, limit=b["limit"] + 50) if b["id"] == "fitts.moves_over_4_bits" else b for b in budgets.load()]
    monkeypatch.setattr(budgets, "load", lambda path=budgets.BUDGETS_PATH: loosened)
    ok, message = report.check_docs(**docs_copy)
    assert not ok and "DRIFT" in message and "budgets.json" in message


def test_editing_the_trace_or_the_snapshot_or_the_markdown_is_caught(docs_copy):
    trace = json.loads(docs_copy["trace_path"].read_text(encoding="utf-8"))
    trace["pointer_passes"][0]["pointer_targets"][3]["to"][0] += 5
    docs_copy["trace_path"].write_bytes(report.dump_trace(trace).encode("utf-8"))
    assert not report.check_docs(**docs_copy)[0]  # trace changed, snapshot not rebuilt
    md = docs_copy["report_path"]
    original = md.read_bytes()
    trace_ok = report.TRACE.read_bytes()
    docs_copy["trace_path"].write_bytes(trace_ok)
    md.write_bytes(original + b"hand edit\n")
    assert not report.check_docs(**docs_copy)[0]
    md.write_bytes(original)
    snap = json.loads(docs_copy["snapshot_path"].read_text(encoding="utf-8"))
    # Always alter the observation, including when the current measured value is zero.
    snap["fitts"]["summary"]["moves_id_over_4"] += 1
    docs_copy["snapshot_path"].write_bytes(report.dumps(snap).encode("utf-8"))
    assert not report.check_docs(**docs_copy)[0]


def test_ui_hash_mismatch_is_a_note_in_the_fast_tier_and_a_failure_when_strict(docs_copy, monkeypatch):
    monkeypatch.setattr(journey, "ui_hashes", lambda: {"app.js": "f" * 64})
    ok, message = report.check_docs(**docs_copy)
    assert ok and "informational" in message  # visual lane may change the UI before refreshing evidence
    ok, message = report.check_docs(strict=True, **docs_copy)
    assert not ok and message.startswith("STALE")  # but stale evidence cannot pass the release tier
