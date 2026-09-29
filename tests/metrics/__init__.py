"""Tests for the metrics lane (quality/metrics).

Machine-dependent checks (wall-clock thresholds, fits of timings, a real uvicorn server, a `pytest --collect-only`
subprocess) carry the `timing` marker below: they are skipped, reported as NOT_RUN, in the fast and full tiers, and run
by the release session `metrics_report` (EIJA_METRICS_TIMING=1). Everything else here is a deterministic function of
the source tree or of synthetic data.
"""
import os

import pytest

timing = pytest.mark.skipif(
    os.environ.get("EIJA_METRICS_TIMING") != "1",
    reason="NOT_RUN: machine-dependent or slow; run by the release session metrics_report (EIJA_METRICS_TIMING=1)",
)
