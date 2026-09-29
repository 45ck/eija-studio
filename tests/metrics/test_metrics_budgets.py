import pytest

from quality.metrics import budgets, collect, inventory
from quality.metrics.common import FAIL, NOT_RUN, PASS


def test_every_budget_is_not_run_on_an_empty_document():
    results = budgets.evaluate({"sections": {}})
    assert {r["status"] for r in results} == {NOT_RUN}  # absence is never a pass
    assert len({r["id"] for r in results}) == len(budgets.BUDGETS)  # ids are unique


def test_operators():
    ops = budgets.OPS
    assert ops["<"](1, 2) and not ops["<"](2, 2) and ops["<="](2, 2) and ops[">="](2, 2) and ops["=="](0, 0)


def test_tiers_are_declared_and_timing_or_machine_budgets_are_release_tier():
    tiers = {b.id: b.tier for b in budgets.BUDGETS}
    assert set(tiers.values()) == {"structural", "release"}
    for b in budgets.BUDGETS:
        if b.kind == "timing" or b.section in {"coverage", "lane_reports"}:
            assert b.tier == "release", b.id  # a machine-dependent number must never gate the fast/full tiers
        else:
            assert b.tier == "structural", b.id


def test_release_budgets_are_not_run_on_a_structural_profile_document():
    """The fast/full sessions collect the structural profile: every release budget must be NOT_RUN there, never PASS or FAIL."""
    skipped = {"status": NOT_RUN, "reason": collect.NOT_COLLECTED}
    doc = {"sections": {name: skipped for name in ("coverage", "lane_reports", "performance", "scaling", "verification_yield")}}
    results = {r["id"]: r["status"] for r in budgets.evaluate(doc)}
    release = {b.id for b in budgets.BUDGETS if b.tier == "release"}
    assert release and {results[i] for i in release} == {NOT_RUN}


def test_coverage_floor_is_the_quality_lanes_not_a_copy():
    cov = next(b for b in budgets.BUDGETS if b.id == "COV-01")
    assert cov.limit == inventory.coverage_floor()
    doc = {"sections": {"coverage": {"status": "MEASURED", "summary": {"percent": cov.limit - 0.5}}}}
    assert next(r for r in budgets.evaluate(doc) if r["id"] == "COV-01")["status"] == FAIL
    doc["sections"]["coverage"]["summary"]["percent"] = cov.limit
    assert next(r for r in budgets.evaluate(doc) if r["id"] == "COV-01")["status"] == PASS


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


@pytest.mark.parametrize(("r2", "exponent", "quad", "expected"), [
    (0.99, 1.0, 0.7, PASS), (0.85, 0.9, 0.5, PASS), (0.6, 1.9, 0.99, FAIL)])
def test_scaling_budgets_distinguish_linear_from_quadratic(r2, exponent, quad, expected):
    doc = {"sections": {"scaling": {"status": "MEASURED", "fit": {
        "two_term_r2": r2, "loglog_exponent": exponent, "r2": r2, "alt_quadratic_r2": quad}}}}
    got = {r["id"]: r["status"] for r in budgets.evaluate(doc)}
    assert got["SCALE-01"] == got["SCALE-02"] == got["SCALE-03"] == expected
