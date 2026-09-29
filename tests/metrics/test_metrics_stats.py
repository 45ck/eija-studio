import random

import pytest

from quality.hci import laws
from quality.metrics import common
from quality.metrics.common import latency_summary, ols, ols_multi, spread


def test_percentiles_are_the_hci_lanes_not_a_second_definition():
    """One collector per metric: nearest-rank percentile and IQR come from quality.hci.laws."""
    data = [10.0, 20.0, 30.0, 40.0]
    assert common.laws is laws and common.DOHERTY_MS == laws.DOHERTY_MS == 400.0
    s = latency_summary(data)
    assert s["p50_ms"] == laws.percentile(data, 50) == 20.0  # nearest rank, no interpolation
    assert (s["p25_ms"], s["p50_ms"], s["p75_ms"]) == laws.iqr(data) == (10.0, 20.0, 30.0)


def test_latency_summary_orders_percentiles_and_reports_the_iqr():
    s = latency_summary([5, 1, 9, 3, 7, 100])
    assert s["n"] == 6 and s["min_ms"] == 1 and s["max_ms"] == 100
    assert s["min_ms"] <= s["p25_ms"] <= s["p50_ms"] <= s["p75_ms"] <= s["p95_ms"] <= s["p99_ms"] <= s["max_ms"]


def test_spread_is_median_and_iqr_of_repeats_never_a_single_run():
    s = spread([5.0, 1.0, 9.0, 3.0, 7.0])
    assert s == {"n": 5, "min": 1.0, "p25": 3.0, "median": 5.0, "p75": 7.0}
    assert spread([2.0]) == {"n": 1, "min": 2.0, "p25": 2.0, "median": 2.0, "p75": 2.0}
    with pytest.raises(ValueError):
        spread([])


# Hand-worked example. x = 1..5, y = 2,3,5,4,6.  mean x = 3, mean y = 4.
#   Sxy = (-2)(-2) + (-1)(-1) + 0(1) + 1(0) + 2(2) = 9,  Sxx = 4+1+0+1+4 = 10  ->  slope 0.9, intercept 4 - 0.9*3 = 1.3
#   fitted 2.2, 3.1, 4.0, 4.9, 5.8; residuals -0.2, -0.1, 1.0, -0.9, 0.2; SS_res = 0.04+0.01+1+0.81+0.04 = 1.9
#   SS_tot = 4+1+1+0+4 = 10  ->  R^2 = 1 - 1.9/10 = 0.81
def test_ols_matches_a_hand_worked_example():
    fit = ols([1, 2, 3, 4, 5], [2, 3, 5, 4, 6])
    assert fit["c1"] == pytest.approx(0.9) and fit["c0"] == pytest.approx(1.3) and fit["r2"] == pytest.approx(0.81)
    assert fit["residuals"] == pytest.approx([-0.2, -0.1, 1.0, -0.9, 0.2])


def test_ols_multi_matches_a_hand_worked_exact_plane():
    """y = 1 + 2*x1 + 3*x2 through five non-collinear points is recovered exactly, R^2 = 1."""
    rows = [[0, 0], [1, 0], [0, 1], [1, 1], [2, 1]]
    fit = ols_multi(rows, [1 + 2 * a + 3 * b for a, b in rows])
    assert fit["beta"] == pytest.approx([1, 2, 3]) and fit["r2"] == pytest.approx(1)


def test_ols_multi_hand_worked_r2_with_a_noisy_plane():
    """Same design, one observation moved by +1: R^2 is 1 - SS_res/SS_tot, computed independently below."""
    rows = [[0, 0], [1, 0], [0, 1], [1, 1], [2, 1]]
    ys = [1, 3, 4, 6, 8 + 1.0]
    fit = ols_multi(rows, ys)
    mean = sum(ys) / len(ys)
    ss_res = sum(r * r for r in fit["residuals"])
    ss_tot = sum((y - mean) ** 2 for y in ys)
    assert fit["r2"] == pytest.approx(1 - ss_res / ss_tot) and 0.9 < fit["r2"] < 1
    assert sum(fit["residuals"]) == pytest.approx(0, abs=1e-9)  # least-squares residuals sum to zero with an intercept


def test_ols_recovers_an_exact_line():
    xs = [1.0, 2.0, 3.0, 4.0, 5.0]
    fit = ols(xs, [2 + 3 * x for x in xs])
    assert fit["c0"] == pytest.approx(2) and fit["c1"] == pytest.approx(3) and fit["r2"] == pytest.approx(1)
    assert all(abs(r) < 1e-9 for r in fit["residuals"])


def test_r2_is_low_for_a_quadratic_negative_control():
    """A detector that always says 'linear' would pass the previous test; this one must fail it."""
    xs = [float(x) for x in range(1, 40)]
    assert ols(xs, [x * x for x in xs])["r2"] < 0.97
    assert ols([x * x for x in xs], [x * x for x in xs])["r2"] == pytest.approx(1)


def test_ols_rejects_too_few_points():
    with pytest.raises(ValueError, match="three"):
        ols([1.0, 2.0], [1.0, 2.0])


def test_ols_multi_recovers_two_coefficients_under_noise():
    rng = random.Random(7)  # noqa: S311 - seeded test data, not security
    rows = [[rng.uniform(1, 100), rng.uniform(1, 100)] for _ in range(60)]
    ys = [1.5 + 0.7 * a + 0.1 * b + rng.gauss(0, 0.05) for a, b in rows]
    fit = ols_multi(rows, ys)
    assert fit["beta"] == pytest.approx([1.5, 0.7, 0.1], abs=0.05) and fit["r2"] > 0.999


def test_ols_multi_detects_collinear_features():
    rows = [[float(i), 2.0 * i] for i in range(1, 10)]
    with pytest.raises(ValueError, match="collinear"):
        ols_multi(rows, [float(i) for i in range(1, 10)])
