import pytest

from eija_studio.domain.impact import closure
from quality.metrics import budgets, scaling
from quality.metrics.common import PASS


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


@pytest.fixture(scope="module")
def measured_scaling():
    return scaling.collect("quick")


@pytest.mark.slow
@pytest.mark.timing
def test_closure_is_measured_linear_on_this_machine(measured_scaling):
    """A real measurement: the two-term fit must explain the timings and growth must be near-linear."""
    fit = measured_scaling["fit"]
    assert fit["two_term_r2"] > 0.9 and 0.8 <= fit["loglog_exponent"] <= 1.2
    assert fit["r2"] > fit["alt_quadratic_r2"]
    assert fit["two_term_cV_ms_per_node"] > 0 and fit["two_term_cE_ms_per_edge"] > 0
    results = {r["id"]: r["status"] for r in budgets.evaluate({"sections": {"scaling": measured_scaling}}) if r["section"] == "scaling"}
    assert set(results) == {"SCALE-01", "SCALE-02", "SCALE-03", "SCALE-04"} and set(results.values()) == {PASS}
