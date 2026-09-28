import random

import pytest

from quality.metrics.common import latency_summary, ols, ols_multi, percentile


def test_percentile_interpolates_and_bounds():
    data = [10.0, 20.0, 30.0, 40.0]
    assert percentile(data, 0) == 10 and percentile(data, 100) == 40
    assert percentile(data, 50) == 25  # linear interpolation between the middle pair
    assert percentile([7.0], 99) == 7
    with pytest.raises(ValueError):
        percentile([], 50)


def test_latency_summary_orders_percentiles():
    s = latency_summary([5, 1, 9, 3, 7, 100])
    assert s["n"] == 6 and s["min_ms"] == 1 and s["max_ms"] == 100
    assert s["p50_ms"] <= s["p95_ms"] <= s["p99_ms"] <= s["max_ms"]


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
    with pytest.raises(ValueError):
        ols([1.0, 2.0], [1.0, 2.0])


def test_ols_multi_recovers_two_coefficients_under_noise():
    rng = random.Random(7)
    rows = [[rng.uniform(1, 100), rng.uniform(1, 100)] for _ in range(60)]
    ys = [1.5 + 0.7 * a + 0.1 * b + rng.gauss(0, 0.05) for a, b in rows]
    fit = ols_multi(rows, ys)
    assert fit["beta"] == pytest.approx([1.5, 0.7, 0.1], abs=0.05) and fit["r2"] > 0.999


def test_ols_multi_detects_collinear_features():
    rows = [[float(i), 2.0 * i] for i in range(1, 10)]
    with pytest.raises(ValueError):
        ols_multi(rows, [float(i) for i in range(1, 10)])
