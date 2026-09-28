"""Committed HCI evidence must be reproducible from its own snapshot (no browser)."""
import json

from quality.hci import report


def test_report_md_is_exactly_the_rendering_of_the_committed_snapshot():
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
