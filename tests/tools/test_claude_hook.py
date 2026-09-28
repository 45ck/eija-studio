"""The noslop PreToolUse hook blocks real bypasses and nothing else (ADR-0036)."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parents[2] / ".claude" / "hooks" / "pre-tool-use.sh"
SH = shutil.which("sh")
NO_VERIFY = "--no" + "-verify"  # assembled so this file itself never contains the literal flag
SKIP = "[skip" + " ci]"

pytestmark = pytest.mark.skipif(SH is None, reason="needs a POSIX sh (Git Bash on Windows)")


def blocked(command: str) -> bool:
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    result = subprocess.run([SH, str(HOOK)], input=payload, capture_output=True, text=True, check=False)  # noqa: S603
    assert result.returncode in (0, 2), result.stderr
    return result.returncode == 2


@pytest.mark.parametrize(
    "command",
    [
        f"git commit -m x {NO_VERIFY}",
        f"git push {NO_VERIFY} origin main",
        f"git -c core.hooksPath=x commit {NO_VERIFY} -m y",
        f'git commit -m "wip {SKIP}"',
    ],
)
def test_real_bypasses_are_blocked(command):
    assert blocked(command)


@pytest.mark.parametrize(
    "command",
    [
        f'gh pr comment 3 --body "we never use {NO_VERIFY} here"',
        f"echo {SKIP}",
        "git worktree remove --force /tmp/scratch",
        "pip install --force-reinstall x",
        "git commit -m 'feat: ordinary change'",
        "git push origin lane/x",
        "nox -t fast",
    ],
)
def test_mentions_and_ordinary_force_operations_are_allowed(command):
    assert not blocked(command)
