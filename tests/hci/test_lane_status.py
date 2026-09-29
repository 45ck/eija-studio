"""The lane verdict that quality.metrics.aggregate reads from reports/hci/report.json (pure logic, no browser)."""
import json
from pathlib import Path

from quality.hci.__main__ import lane_status, write_lane_report


def test_a_regressed_budget_fails_the_lane_and_a_documented_gap_does_not():
    assert lane_status({"budgets": [{"status": "PASS"}, {"status": "GAP"}]}) == "PASS"
    assert lane_status({"budgets": [{"status": "PASS"}, {"status": "GAP"}, {"status": "FAIL"}]}) == "FAIL"


def test_every_writer_of_the_lane_report_stamps_the_verdict(tmp_path):
    """The pytest fixture used to write report.json without `status`, so quality.metrics read UNKNOWN and LANE-01 failed."""
    write_lane_report({"budgets": [{"status": "GAP"}]}, tmp_path)
    assert json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))["status"] == "PASS"


def test_the_pytest_fixture_writes_the_lane_report_through_the_stamping_writer():
    src = Path(__file__).with_name("conftest.py").read_text(encoding="utf-8")
    assert "write_lane_report(" in src
    assert 'out / "report.json"' not in src
