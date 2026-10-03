"""Repository facts rendering checks; not browser or human evidence."""
from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest
from eija_studio.adapters.providers.process import resolve_command, run_bounded

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.skipif(shutil.which("node") is None, reason="NOT_RUN: Node is not installed")
def test_repository_source_presentation_contracts() -> None:
    """Preserve missingness, source limits and hostile text in the real renderer."""
    node = shutil.which("node")
    assert node is not None
    result = run_bounded(
        [*resolve_command(node), "--test", str(ROOT / "tests" / "web" / "source.test.cjs")],
        cwd=str(ROOT), input=None, env=dict(os.environ), timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
