import pytest

from quality.metrics import perf


def test_run_flow_treats_a_non_200_as_an_error_not_a_sample():
    def failing(method, path, body=None):
        return 500, 1.0, {"code": "boom"}
    with pytest.raises(RuntimeError, match="HTTP 500"):
        perf.run_flow(failing, 0, {})


def test_endpoint_report_classifies_kind_and_threshold_bands():
    rep = perf.endpoints_report({"GET /a": [5.0] * 10, "POST /api/cases/{id}/verify": [1000.0] * 10,
                                 "POST /b": [150.0] * 10})
    rows = {r["endpoint"]: r for r in rep["endpoints"]}
    assert rows["GET /a"]["kind"] == "read" and rows["GET /a"]["p95_within_instant"]
    assert rows["POST /b"]["kind"] == "write" and not rows["POST /b"]["p95_within_instant"]
    assert rows["POST /b"]["p95_within_doherty"]
    verify = rows["POST /api/cases/{id}/verify"]
    assert verify["kind"] == "compute" and not verify["p95_within_doherty"]
    assert rep["summary"]["over_doherty"] == ["POST /api/cases/{id}/verify"]


@pytest.mark.slow
@pytest.mark.timing
@pytest.mark.parametrize("opener", [perf.testclient_call, perf.uvicorn_call], ids=["testclient", "real-uvicorn"])
def test_interactive_endpoints_have_median_latency_under_the_doherty_threshold(opener):
    """Smoke-sized measurement (three journeys, 6 reads): with so few samples p95 is just the maximum and one slow
    disk flush on a busy machine would make it flaky, so this guard uses the median (robust to one outlier). The p95 budgets are
    evaluated over the larger quick/full profiles (nox -s metrics). The second case starts a real uvicorn
    server on an ephemeral loopback port."""
    report = perf.measure_transport(opener, "smoke")
    assert {r["kind"] for r in report["endpoints"]} == {"read", "write", "compute"}
    interactive = [r for r in report["endpoints"] if r["kind"] in ("read", "write")]
    assert interactive and max(r["p50_ms"] for r in interactive) < perf.DOHERTY_MS
    verify = next(r for r in report["endpoints"] if r["kind"] == "compute")
    assert verify["p50_ms"] < 10_000  # long-running compute step, budgeted separately (see README)
    assert all(r["n"] >= 1 for r in report["endpoints"])


def test_identity_harness_keeps_real_hashing_but_marks_the_override():
    ident = perf.harness_identity()
    assert ident["trusted_fixture"] is True and ident["identity_source"] == "metrics-harness"
    assert len(ident["implementation"]) == 64
