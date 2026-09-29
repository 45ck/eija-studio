import json

import pytest

from quality.metrics import budgets, inventory
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


@pytest.mark.slow
def test_real_inventory_attributes_layers_and_matches_pytest_collection():
    inv = inventory.collect()
    assert inv["status"] == MEASURED
    layers = {r["layer"]: r for r in inv["by_layer"]}
    assert layers["domain"]["tests_direct"] > 0 and layers["interfaces"]["files_direct"] >= 1
    assert layers["domain"]["tests_transitive"] >= layers["domain"]["tests_direct"]
    # The whole-repo static count and pytest's own collection can differ legitimately (dynamic parametrisation in
    # other lanes' tests, modules that skip at import for a missing extra); the summary reports both and whether
    # they match. The exact comparison is made on files whose parametrisation is literal (next test).
    summary = inv["summary"]
    assert summary["tests_collected_by_pytest"] > 0 and summary["static_matches_collected"] in (True, False)
    assert summary["static_matches_collected"] == (summary["tests_collected_by_pytest"] == summary["tests_static"])


@pytest.mark.slow
def test_static_count_equals_pytest_collection_where_parametrisation_is_literal():
    """Negative control for the ast counter: this lane's own tests use literal parametrisation only."""
    static = sum(r["tests"] for r in inventory.collect(run_pytest_collection=False)["files"] if r["file"].startswith("tests/metrics/"))
    assert inventory.collected_count(paths=("tests/metrics",)) == static


def test_coverage_is_not_run_without_a_report_and_never_zero(monkeypatch, tmp_path):
    monkeypatch.setattr(inventory, "COVERAGE_JSON", tmp_path / "missing.json")
    cov = inventory.collect_coverage()
    assert cov["status"] == NOT_RUN and "coverage" in cov["reason"]


def bound_report(monkeypatch, tmp_path, report, *, recorded="tree-A", current="tree-A"):
    """Write a coverage.json plus the sidecar that binds it to a tree fingerprint (`recorded`)."""
    path, meta = tmp_path / "coverage.json", tmp_path / "coverage.meta.json"
    path.write_text(json.dumps(report), encoding="utf-8")
    if recorded is not None:
        meta.write_text(json.dumps({"tree_sha256": recorded}), encoding="utf-8")
    monkeypatch.setattr(inventory, "COVERAGE_JSON", path)
    monkeypatch.setattr(inventory, "COVERAGE_META", meta)
    monkeypatch.setattr(inventory, "tree_fingerprint", lambda: current)
    return path


MINIMAL_REPORT = {"meta": {"version": "7.x"}, "files": {}, "totals": {"num_statements": 0, "covered_lines": 0, "percent_covered": 100.0}}


def test_coverage_from_another_tree_is_stale_not_run_and_its_budget_never_passes(monkeypatch, tmp_path):
    """Regression: COV-01 used to PASS on a coverage.json measured before the code changed."""
    bound_report(monkeypatch, tmp_path, MINIMAL_REPORT, recorded="tree-A", current="tree-B")
    cov = inventory.collect_coverage()
    assert cov["status"] == NOT_RUN and "stale" in cov["reason"]
    assert next(r for r in budgets.evaluate({"sections": {"coverage": cov}}) if r["id"] == "COV-01")["status"] == NOT_RUN


def test_coverage_without_a_binding_sidecar_is_not_run(monkeypatch, tmp_path):
    bound_report(monkeypatch, tmp_path, MINIMAL_REPORT, recorded=None)
    assert inventory.collect_coverage()["status"] == NOT_RUN


LF_SOURCE = b"x = 1" + bytes([10])


def test_tree_fingerprint_changes_with_source_and_ignores_line_endings(monkeypatch, tmp_path):
    (tmp_path / "src" / "eija_studio").mkdir(parents=True)
    (tmp_path / "tests").mkdir()
    mod = tmp_path / "src" / "eija_studio" / "m.py"
    monkeypatch.setattr(inventory, "ROOT", tmp_path)
    monkeypatch.setattr(inventory, "SRC", tmp_path / "src" / "eija_studio")
    monkeypatch.setattr(inventory, "TESTS", tmp_path / "tests")
    mod.write_bytes(LF_SOURCE)
    first = inventory.tree_fingerprint()
    mod.write_bytes(LF_SOURCE.replace(bytes([10]), bytes([13, 10])))
    assert inventory.tree_fingerprint() == first  # CRLF checkout of the same content is the same tree
    mod.write_bytes(LF_SOURCE.replace(b"1", b"2"))
    assert inventory.tree_fingerprint() != first


def test_coverage_report_is_aggregated_per_layer(monkeypatch, tmp_path):
    def entry(n, cov, br, cbr):
        return {"summary": {"num_statements": n, "covered_lines": cov, "missing_lines": n - cov,
                            "percent_covered": 100 * (cov + cbr) / (n + br), "num_branches": br, "covered_branches": cbr}}
    report = {"meta": {"version": "7.x"}, "files": {
        "src\\eija_studio\\domain\\models.py": entry(100, 90, 10, 8),
        "src\\eija_studio\\domain\\policy.py": entry(50, 25, 0, 0),
        "src\\eija_studio\\adapters\\receipts.py": entry(10, 10, 0, 0)},
        "totals": {"num_statements": 160, "covered_lines": 125, "percent_covered": 78.0, "num_branches": 10, "covered_branches": 8}}
    bound_report(monkeypatch, tmp_path, report)
    cov = inventory.collect_coverage()
    layers = {r["layer"]: r for r in cov["layers"]}
    assert layers["domain"]["statements"] == 150 and layers["domain"]["covered"] == 115
    assert layers["adapters"]["line_percent"] == 100.0
    assert cov["summary"]["percent"] == 78.0
