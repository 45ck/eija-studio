import json

from quality.metrics import inventory
from quality.metrics.common import MEASURED, NOT_RUN


def test_scan_file_counts_tests_asserts_raises_and_parametrization(tmp_path, monkeypatch):
    monkeypatch.setattr(inventory, "rel", lambda p: p.name)  # tmp file lives outside the repository
    f = tmp_path / "test_sample.py"
    f.write_text(
        "import pytest\nfrom eija_studio.domain.models import canonical\n"
        "@pytest.mark.parametrize('x', [1, 2, 3])\n"
        "def test_a(x):\n    assert x\n    assert canonical(x)\n"
        "def test_b():\n    with pytest.raises(ValueError):\n        int('z')\n"
        "def helper():\n    assert False\n",
        encoding="utf-8")
    row = inventory.scan_file(f)
    assert row["tests"] == 4 and row["test_functions"] == 2  # 3 parametrised + 1
    assert row["asserts"] == 2 and row["raises_blocks"] == 1  # helper() is not a test
    assert "eija_studio.domain.models" in row["imports"]


def test_real_inventory_attributes_layers_and_matches_pytest_collection():
    inv = inventory.collect()
    assert inv["status"] == MEASURED
    layers = {r["layer"]: r for r in inv["by_layer"]}
    assert layers["domain"]["tests_direct"] > 0 and layers["interfaces"]["files_direct"] >= 1
    assert layers["domain"]["tests_transitive"] >= layers["domain"]["tests_direct"]
    # static ast count vs pytest's own collection: equal unless a test parametrises dynamically
    assert abs(inv["summary"]["tests_collected_by_pytest"] - inv["summary"]["tests_static"]) <= 5


def test_coverage_is_not_run_without_a_report_and_never_zero(monkeypatch, tmp_path):
    monkeypatch.setattr(inventory, "COVERAGE_JSON", tmp_path / "missing.json")
    cov = inventory.collect_coverage()
    assert cov["status"] == NOT_RUN and "coverage" in cov["reason"]


def test_coverage_report_is_aggregated_per_layer(monkeypatch, tmp_path):
    def entry(n, cov, br, cbr):
        return {"summary": {"num_statements": n, "covered_lines": cov, "missing_lines": n - cov,
                            "percent_covered": 100 * (cov + cbr) / (n + br), "num_branches": br, "covered_branches": cbr}}
    report = {"meta": {"version": "7.x"}, "files": {
        "src\\eija_studio\\domain\\models.py": entry(100, 90, 10, 8),
        "src\\eija_studio\\domain\\policy.py": entry(50, 25, 0, 0),
        "src\\eija_studio\\adapters\\receipts.py": entry(10, 10, 0, 0)},
        "totals": {"num_statements": 160, "covered_lines": 125, "percent_covered": 78.0, "num_branches": 10, "covered_branches": 8}}
    path = tmp_path / "coverage.json"
    path.write_text(json.dumps(report), encoding="utf-8")
    monkeypatch.setattr(inventory, "COVERAGE_JSON", path)
    cov = inventory.collect_coverage()
    layers = {r["layer"]: r for r in cov["layers"]}
    assert layers["domain"]["statements"] == 150 and layers["domain"]["covered"] == 115
    assert layers["adapters"]["line_percent"] == 100.0
    assert cov["summary"]["percent"] == 78.0
