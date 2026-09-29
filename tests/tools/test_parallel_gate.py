"""pytest-xdist switch (quality/tools/parallel.py): fallbacks, plus a negative control that parallel runs still fail."""
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from quality.tools import parallel

PASSING = "def test_a(): pass\ndef test_b(): pass\ndef test_c(): pass\n"
PLANTED = "def test_planted_defect():\n    assert 1 == 2  # planted: a parallel run must not hide this\n"


def test_serial_env_var_forces_no_xdist_arguments(monkeypatch):
    monkeypatch.setenv("EIJA_SERIAL", "1")
    assert parallel.xdist_args() == []


def test_missing_xdist_falls_back_to_serial(monkeypatch):
    monkeypatch.delenv("EIJA_SERIAL", raising=False)
    monkeypatch.setattr(parallel, "xdist_available", lambda: False)
    assert parallel.xdist_args() == []


def test_default_is_four_workers_loadfile(monkeypatch):
    monkeypatch.delenv("EIJA_SERIAL", raising=False)
    monkeypatch.delenv("EIJA_XDIST_WORKERS", raising=False)
    monkeypatch.setattr(parallel, "xdist_available", lambda: True)
    assert parallel.xdist_args() == ["-n", "4", "--dist", "loadfile"]


@pytest.mark.parametrize("workers", ["0", "1", "many", ""])
def test_unusable_worker_count_falls_back_to_serial(monkeypatch, workers):
    monkeypatch.delenv("EIJA_SERIAL", raising=False)
    monkeypatch.setenv("EIJA_XDIST_WORKERS", workers)
    monkeypatch.setattr(parallel, "xdist_available", lambda: True)
    assert parallel.xdist_args() == []


def test_hypothesis_default_profile_is_derandomized():
    """Hypothesis examples must not depend on which xdist worker or which run draws them (the deep profile is the opt-out)."""
    settings = pytest.importorskip("hypothesis").settings
    if os.environ.get("EIJA_HYPOTHESIS_PROFILE") == "deep":
        pytest.skip("the release-tier deep profile is deliberately random")
    assert settings.default.derandomize is True
    assert settings.default.database is None


def _nested(tmp_path: Path, extra: list[str]) -> tuple[int, dict[str, int]]:
    """Run a tiny separate pytest project; return its exit code and its summary counts (passed, failed, ...)."""
    (tmp_path / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k != "PYTEST_ADDOPTS"}
    run = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-c", "pytest.ini", *extra],  # noqa: S603 - fixed argv
                         cwd=tmp_path, env=env, capture_output=True, text=True, check=False, timeout=120)
    counts = {word: int(n) for n, word in re.findall(r"(\d+) (passed|failed|error|errors)", run.stdout.splitlines()[-1])}
    return run.returncode, counts


@pytest.mark.skipif(not parallel.xdist_available(), reason="NOT_RUN: pytest-xdist not installed")
def test_planted_failure_fails_under_xdist_with_the_same_counts_as_serial(tmp_path):
    (tmp_path / "test_ok.py").write_text(PASSING, encoding="utf-8")
    (tmp_path / "test_planted.py").write_text(PLANTED, encoding="utf-8")
    serial = _nested(tmp_path, [])
    parallel_run = _nested(tmp_path, ["-n", "2", "--dist", "loadfile"])
    assert serial == (1, {"passed": 3, "failed": 1})
    assert parallel_run == serial  # the failure is not lost, and no test is dropped or run twice
