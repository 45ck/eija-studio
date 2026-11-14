"""The generated-law SMT gate proves its packs in parallel (17.5 min serial over 11 packs on 2026-11-14, 5.3 min on
4 processes, byte-identical reports); EIJA_SERIAL=1 keeps the old one-process run."""
from __future__ import annotations

import pytest

from verification.smt import laws


@pytest.mark.parametrize("env,jobs,expected", [
    ({}, 11, laws.DEFAULT_WORKERS), ({}, 2, 2), ({"EIJA_SERIAL": "1"}, 11, 1), ({"EIJA_SMT_WORKERS": "8"}, 11, 8),
    ({"EIJA_SMT_WORKERS": "0"}, 11, 1), ({"EIJA_SMT_WORKERS": "lots"}, 11, laws.DEFAULT_WORKERS), ({}, 0, 1)])
def test_worker_count(monkeypatch, env, jobs, expected):
    for name in ("EIJA_SERIAL", "EIJA_SMT_WORKERS"):
        monkeypatch.delenv(name, raising=False)
    for name, value in env.items():
        monkeypatch.setenv(name, value)
    assert laws._workers(jobs) == expected
