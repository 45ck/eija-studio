from quality.metrics import budgets
from quality.metrics.common import FAIL, NOT_RUN, PASS


def test_every_budget_is_not_run_on_an_empty_document():
    results = budgets.evaluate({"sections": {}})
    assert {r["status"] for r in results} == {NOT_RUN}  # absence is never a pass
    assert len({r["id"] for r in results}) == len(budgets.BUDGETS)  # ids are unique


def test_operators():
    ops = budgets.OPS
    assert ops["<"](1, 2) and not ops["<"](2, 2) and ops["<="](2, 2) and ops[">="](2, 2) and ops["=="](0, 0)


def test_timing_budgets_pass_and_fail_on_synthetic_measurements():
    def doc(p95):
        endpoints = [{"endpoint": "GET /x", "kind": "read", "p95_ms": p95},
                     {"endpoint": "POST /y", "kind": "write", "p95_ms": 10.0},
                     {"endpoint": "POST /verify", "kind": "compute", "p95_ms": 1500.0}]
        return {"sections": {"performance": {"status": "MEASURED", "verify_scaling": {"r2": 0.99}, "transports": {
            "testclient": {"status": "MEASURED", "endpoints": endpoints},
            "uvicorn": {"status": "NOT_RUN", "reason": "x"}}}}}
    fast = {r["id"]: r["status"] for r in budgets.evaluate(doc(50.0))}
    slow = {r["id"]: r["status"] for r in budgets.evaluate(doc(450.0))}
    assert fast["PERF-01"] == PASS and slow["PERF-01"] == FAIL
    assert fast["PERF-04"] == PASS  # a 1.5 s verify is inside the 10 s long-running budget
    assert fast["PERF-03"] == NOT_RUN  # uvicorn transport not measured: no verdict


def test_scaling_budgets_distinguish_linear_from_quadratic():
    def doc(r2, exponent, quad):
        return {"sections": {"scaling": {"status": "MEASURED", "fit": {
            "two_term_r2": r2, "loglog_exponent": exponent, "r2": r2, "alt_quadratic_r2": quad}}}}
    good = {r["id"]: r["status"] for r in budgets.evaluate(doc(0.99, 1.0, 0.7))}
    bad = {r["id"]: r["status"] for r in budgets.evaluate(doc(0.6, 1.9, 0.99))}
    assert good["SCALE-01"] == good["SCALE-02"] == good["SCALE-03"] == PASS
    assert bad["SCALE-01"] == bad["SCALE-02"] == bad["SCALE-03"] == FAIL
