import pytest

from quality.metrics import perf

from . import timing


def test_run_flow_treats_a_non_200_as_an_error_not_a_sample():
    def failing(method, path, body=None):
        return 500, 1.0, {"code": "boom"}
    with pytest.raises(RuntimeError, match="HTTP 500"):
        perf.run_flow(failing, 0, {})


def test_endpoint_report_classifies_kind_threshold_bands_and_reports_the_iqr():
    rep = perf.endpoints_report({"GET /a": [5.0] * 10, "POST /api/cases/{id}/verify": [1000.0] * 10,
                                 "POST /b": [150.0] * 10})
    rows = {r["endpoint"]: r for r in rep["endpoints"]}
    assert rows["GET /a"]["kind"] == "read" and rows["GET /a"]["p95_within_instant"]
    assert rows["POST /b"]["kind"] == "write" and not rows["POST /b"]["p95_within_instant"]
    assert rows["POST /b"]["p95_within_doherty"]
    assert (rows["POST /b"]["p25_ms"], rows["POST /b"]["p50_ms"], rows["POST /b"]["p75_ms"]) == (150.0, 150.0, 150.0)
    verify = rows["POST /api/cases/{id}/verify"]
    assert verify["kind"] == "compute" and not verify["p95_within_doherty"]
    assert rep["summary"]["over_doherty"] == ["POST /api/cases/{id}/verify"]


def test_doherty_constant_is_the_hci_lanes():
    from quality.hci import laws
    assert perf.DOHERTY_MS == laws.DOHERTY_MS


def test_testclient_smoke_pipeline_reaches_every_endpoint_kind():
    """Pipeline check only: the journey runs against the real app and every endpoint kind is sampled. No latency threshold
    here (that is machine-dependent, see the timing tests below and docs/metrics/README.md)."""
    report = perf.measure_transport(perf.testclient_call, "smoke")
    assert {r["kind"] for r in report["endpoints"]} == {"read", "write", "compute"}
    assert all(r["n"] >= 1 and r["min_ms"] <= r["p25_ms"] <= r["p50_ms"] <= r["p75_ms"] <= r["max_ms"] for r in report["endpoints"])


@timing
@pytest.mark.parametrize("opener", [perf.testclient_call, perf.uvicorn_call], ids=["testclient", "real-uvicorn"])
def test_interactive_endpoints_have_median_latency_under_the_doherty_threshold(opener):
    """Release tier. Smoke-sized (two samples per read): p95 would be the maximum and one slow disk flush on a busy machine
    would flake it, so this guard uses the median. The second case starts a real uvicorn server on an ephemeral loopback port."""
    report = perf.measure_transport(opener, "smoke")
    interactive = [r for r in report["endpoints"] if r["kind"] in ("read", "write")]
    assert interactive and max(r["p50_ms"] for r in interactive) < perf.DOHERTY_MS
    verify = next(r for r in report["endpoints"] if r["kind"] == "compute")
    assert verify["p50_ms"] < 10_000  # long-running compute step, budgeted separately (see README)


def test_identity_harness_keeps_real_hashing_but_marks_the_override():
    ident = perf.harness_identity()
    assert ident["trusted_fixture"] is True and ident["identity_source"] == "metrics-harness"
    assert len(ident["implementation"]) == 64
