"""Isolated IDE projection/adapter checks, not browser or human evidence."""
from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest
from eija_studio.adapters.providers.process import resolve_command, run_bounded

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.skipif(shutil.which("node") is None, reason="NOT_RUN: Node is not installed")
@pytest.mark.parametrize("suite", ["shell", "focus-layout", "evidence-overview", "compare", "source-freshness", "tree-navigation", "task-navigation", "task-layout", "repository-review", "repository-navigation", "comparison-navigation"])
def test_ide_source_history_and_review_adapters(suite: str) -> None:
    """Run actual client functions with deterministic isolated DOM/server doubles."""
    node = shutil.which("node")
    assert node is not None
    result = run_bounded(
        [*resolve_command(node), "--test", str(ROOT / "tests" / "web" / f"{suite}.test.cjs")],
        cwd=str(ROOT), input=None, env=dict(os.environ), timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
