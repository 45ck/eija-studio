import math

import pytest

from eija_studio.domain.impact import closure
from quality.metrics import budgets, scaling
from quality.metrics.common import PASS

from . import timing


def test_synthetic_graph_is_seeded_reachable_and_sized():
    g1, e1 = scaling.synthetic_graph(300, 3)
    g2, e2 = scaling.synthetic_graph(300, 3)
    assert (g1, e1) == (g2, e2)  # deterministic
    assert e1 == sum(len(v) for v in g1.values()) == 900
    result = closure(g1, ["n0"])
    assert result["complete"] and len(result["affected"]) == 300
    assert scaling.synthetic_graph(300, 3, seed=1)[0] != g1


def test_fit_report_recognises_linear_and_rejects_quadratic_growth():
    def points(cost):
        # edge density varies (1x, 2x, 4x nodes) so that V and E are not collinear
        return [{"V": v, "E": v * (1, 2, 4)[i % 3], "size": v + v * (1, 2, 4)[i % 3], "degree": (1, 2, 4)[i % 3],
                 "ms": cost(v + v * (1, 2, 4)[i % 3])} for i, v in enumerate((100, 200, 400, 800, 1600, 3200, 6400))]
    assert scaling.fit_report(points(lambda n: 0.5 + 0.001 * n))["r2"] > 0.999  # a fixed overhead is fine for R^2
    linear = scaling.fit_report(points(lambda n: 0.001 * n))
    assert linear["r2"] > 0.999 and linear["loglog_exponent"] == pytest.approx(1, abs=0.15)
    quad = scaling.fit_report(points(lambda n: 1e-6 * n * n))
    assert quad["loglog_exponent"] == pytest.approx(2, abs=0.05) and quad["alt_quadratic_r2"] > quad["r2"]


def test_fit_states_its_hypothesis_and_computes_the_node_to_edge_ratio():
    """Nodes cost 3x an edge here by construction: the printed reading must come from the fit, not from prose."""
    pts = [{"V": v, "E": v * d, "size": v + v * d, "degree": d, "ms": 3 * v + 1 * v * d}
           for v in (100, 400, 1600, 6400) for d in (1, 2, 4)]
    fit = scaling.fit_report(pts)
    assert fit["node_to_edge_cost_ratio"] == pytest.approx(3, rel=1e-3) and fit["two_term_r2"] == pytest.approx(1)
    assert "O(V+E)" in fit["hypothesis"] and "3.0 times" in fit["reading"]


def test_time_call_returns_every_sample_so_callers_can_report_median_and_iqr():
    samples = scaling.time_call(lambda: sum(range(1000)), 5)
    assert len(samples) == 5 and all(s > 0 for s in samples)


def test_smoke_pipeline_records_median_and_iqr_per_point():
    """Structure only (no timing threshold): every point carries the fastest run AND the median and IQR of its repeats."""
    section = scaling.collect("smoke")
    assert section["status"] == "MEASURED" and len(section["points"]) == 6 and section["repeats"] == 3
    for p in section["points"]:
        assert p["ms"] <= p["p25_ms"] <= p["median_ms"] <= p["p75_ms"]
        assert p["size"] == p["V"] + p["E"]
    fit = section["fit"]
    assert all(math.isfinite(fit[k]) for k in ("r2", "two_term_r2", "loglog_exponent", "alt_quadratic_r2"))


@timing
def test_closure_is_measured_linear_on_this_machine():
    """Release tier. A real measurement on the reference machine: the two-term fit explains the timings and growth is near-linear."""
    section = scaling.collect("quick")
    fit = section["fit"]
    assert fit["two_term_r2"] > 0.8 and 0.7 <= fit["loglog_exponent"] <= 1.3
    assert fit["r2"] > fit["alt_quadratic_r2"]
    assert fit["two_term_cV_ms_per_node"] > 0 and fit["two_term_cE_ms_per_edge"] > 0
    results = {r["id"]: r["status"] for r in budgets.evaluate({"sections": {"scaling": section}}) if r["section"] == "scaling"}
    assert set(results.values()) == {PASS}
