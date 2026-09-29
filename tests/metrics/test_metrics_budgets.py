import json
from types import SimpleNamespace

from quality.metrics import budgets
from quality.metrics.__main__ import cmd_check
from quality.metrics.common import FAIL, NOT_RUN, PASS


def test_every_budget_is_not_run_on_an_empty_document():
    results = budgets.evaluate({"sections": {}})
    assert {r["status"] for r in results} == {NOT_RUN}  # absence is never a pass
    assert len({r["id"] for r in results}) == len(budgets.BUDGETS)  # ids are unique


def test_operators():
    ops = budgets.OPS
    assert ops["<"](1, 2) and not ops["<"](2, 2) and ops["<="](2, 2) and ops[">="](2, 2) and ops["=="](0, 0)


def perf_doc(p95, r2=0.99, quad=0.9):
    endpoints = [{"endpoint": "GET /x", "kind": "read", "p95_ms": p95},
                 {"endpoint": "POST /y", "kind": "write", "p95_ms": 10.0},
                 {"endpoint": "POST /verify", "kind": "compute", "p95_ms": 1500.0}]
    return {"sections": {"performance": {"status": "MEASURED", "verify_scaling": {"r2": r2, "alt_quadratic_r2": quad},
                                         "transports": {"testclient": {"status": "MEASURED", "endpoints": endpoints},
                                                        "uvicorn": {"status": "NOT_RUN", "reason": "x"}}}}}


def test_timing_budgets_pass_and_fail_on_synthetic_measurements():
    fast = {r["id"]: r["status"] for r in budgets.evaluate(perf_doc(50.0))}
    slow = {r["id"]: r["status"] for r in budgets.evaluate(perf_doc(450.0))}
    assert fast["PERF-01"] == PASS and slow["PERF-01"] == FAIL
    assert fast["PERF-04"] == PASS  # a 1.5 s verify is inside the 10 s long-running budget
    assert fast["PERF-03"] == NOT_RUN  # uvicorn transport not measured: no verdict


def test_scaling_budgets_distinguish_linear_from_quadratic():
    def doc(r2, exponent, quad):
        return {"sections": {"scaling": {"status": "MEASURED", "fit": {
            "two_term_r2": r2, "loglog_exponent": exponent, "r2": r2, "alt_quadratic_r2": quad}}}}
    good = {r["id"]: r["status"] for r in budgets.evaluate(doc(0.99, 1.0, 0.7))}
    bad = {r["id"]: r["status"] for r in budgets.evaluate(doc(0.6, 1.9, 0.99))}
    assert good["SCALE-01"] == good["SCALE-02"] == good["SCALE-03"] == good["SCALE-04"] == PASS
    assert bad["SCALE-01"] == bad["SCALE-02"] == bad["SCALE-03"] == bad["SCALE-04"] == FAIL


def test_the_requested_single_term_model_is_budgeted_separately_from_the_two_term_model():
    """Regression: only the two-term fit was budgeted, which hid a weaker fit of the model that was asked for."""
    doc = {"sections": {"scaling": {"status": "MEASURED", "fit": {
        "two_term_r2": 0.99, "r2": 0.7, "loglog_exponent": 1.0, "alt_quadratic_r2": 0.5}}}}
    status = {r["id"]: r["status"] for r in budgets.evaluate(doc)}
    assert status["SCALE-01"] == PASS and status["SCALE-04"] == FAIL


def test_verify_scaling_must_beat_its_quadratic_alternative():
    ok = {r["id"]: r["status"] for r in budgets.evaluate(perf_doc(50.0, r2=0.95, quad=0.90))}
    worse = {r["id"]: r["status"] for r in budgets.evaluate(perf_doc(50.0, r2=0.91, quad=0.99))}
    assert ok["PERF-05"] == ok["PERF-06"] == PASS and worse["PERF-06"] == FAIL


def test_timing_budgets_are_advisory_for_the_full_gate_and_enforced_for_the_release_gate(tmp_path, capsys):
    path = tmp_path / "metrics.json"
    path.write_text(json.dumps(perf_doc(900.0)), encoding="utf-8")
    assert cmd_check(SimpleNamespace(input=path, fail_on="structural")) == 0
    assert "advisory" in capsys.readouterr().out
    assert cmd_check(SimpleNamespace(input=path, fail_on="all")) == 1
    structural = {"sections": {"lane_reports": {"status": "MEASURED", "groups": [{"group": "formal", "status": "FAIL"}]}}}
    path.write_text(json.dumps(structural), encoding="utf-8")
    assert cmd_check(SimpleNamespace(input=path, fail_on="structural")) == 1  # a structural FAIL always gates
