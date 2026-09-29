"""The smt-bmc nox sessions: the release tier runs the lane's negative controls too (review of PR #25)."""
from __future__ import annotations

import pytest

from quality.sessions import smt_bmc


class _RecordingSession:
    posargs: list[str] = []  # noqa: RUF012

    def __init__(self):
        self.commands = []

    def run(self, *args, **kwargs):
        self.commands.append(args)

    def skip(self, reason):
        raise AssertionError(reason)


@pytest.mark.parametrize(
    ("session", "tests_file"),
    [("formal_smt_release", "tests/test_formal_smt.py"), ("bmc_deep", "tests/test_formal_bmc.py")],
)
def test_release_sessions_run_the_formal_negative_controls(session, tests_file):
    """`-m 'not formal'` is the default: a release run of only the CLI would never prove the gate detects a fault."""
    recorded = _RecordingSession()
    getattr(smt_bmc, session).func(recorded)
    assert any(cmd[1:3] == ("-m", "pytest") and "formal" in cmd and tests_file in cmd for cmd in recorded.commands), recorded.commands
