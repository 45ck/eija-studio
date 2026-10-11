"""Generated sender protocol checks with window/HTTP doubles; no observed-browser evidence claim."""
from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

from eija_studio.adapters.providers.process import resolve_command, run_bounded

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.skipif(shutil.which("node") is None, reason="NOT_RUN: Node is not installed")
def test_generated_runtime_sender_contracts() -> None:
    """Run the actual sender and action handler with deterministic isolated transport doubles."""
    node = shutil.which("node")
    assert node is not None
    result = run_bounded(
        [*resolve_command(node), "--test", str(ROOT / "tests/web/generated-runtime.test.cjs")],
        cwd=str(ROOT), input=None, env=dict(os.environ), timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
