"""Isolated IDE projection/adapter checks, not browser or human evidence."""
from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest
from eija_studio.adapters.providers.process import resolve_command, run_bounded

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.skipif(shutil.which("node") is None, reason="NOT_RUN: Node is not installed")
def test_ide_source_history_and_review_adapters() -> None:
    """Run actual client functions with deterministic isolated DOM/server doubles."""
    node = shutil.which("node")
    assert node is not None
    result = run_bounded(
        [*resolve_command(node), "--test", str(ROOT / "tests" / "web" / "shell.test.cjs")],
        cwd=str(ROOT), input=None, env=dict(os.environ), timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
