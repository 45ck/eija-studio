"""The lane verdict that quality.metrics.aggregate reads from reports/hci/report.json (pure logic, no browser)."""
from quality.hci.__main__ import lane_status


def test_a_regressed_budget_fails_the_lane_and_a_documented_gap_does_not():
    assert lane_status({"budgets": [{"status": "PASS"}, {"status": "GAP"}]}) == "PASS"
    assert lane_status({"budgets": [{"status": "PASS"}, {"status": "GAP"}, {"status": "FAIL"}]}) == "FAIL"
