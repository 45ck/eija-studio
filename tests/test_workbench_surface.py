"""Dependency-free frontend transaction checks; no browser or human evidence claim."""
from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest
from eija_studio.adapters.providers.process import resolve_command, run_bounded

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.skipif(shutil.which("node") is None, reason="NOT_RUN: Node is not installed")
def test_workbench_transaction_and_layout_contracts() -> None:
    """Execute the real frontend orchestration against isolated server doubles."""
    node = shutil.which("node")
    assert node is not None
    result = run_bounded(
        [*resolve_command(node), "--test", str(ROOT / "tests" / "web" / "workbench.test.cjs")],
        cwd=str(ROOT), input=None, env=dict(os.environ), timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
