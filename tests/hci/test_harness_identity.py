"""ADR-0040: the harness identity stand-in must stay outside src/ and must never weaken the release gate."""
import subprocess
import sys
from pathlib import Path

import pytest

from quality.hci import serve_harness, server

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "eija_studio"


def test_nothing_in_the_shipped_package_knows_the_harness():
    """The stand-in is injected from outside (like tests/conftest.py); src/ must not accept or name it."""
    offenders = [
        str(p.relative_to(ROOT))
        for p in SRC.rglob("*.py")
        if any(token in p.read_text(encoding="utf-8") for token in ("pytest-harness", "serve_harness", "quality.hci", "HARNESS"))
    ]
    assert not offenders


def test_harness_identity_is_a_labelled_stand_in():
    identity = serve_harness.harness_identity()
    assert identity["trusted_fixture"] is True
    assert identity["identity_source"] == "pytest-harness"  # same label tests/conftest.py stamps
    assert serve_harness.HARNESS_MARK == "pytest-harness"


def test_harness_refuses_workspaces_outside_the_scratch_root(tmp_path):
    with pytest.raises(SystemExit, match="refusing workspace"):
        serve_harness.check_workspace(tmp_path / "ws")  # pytest temp lives under .tmp/ but not under .tmp/hci/
    with pytest.raises(SystemExit, match="refusing workspace"):
        serve_harness.check_workspace(ROOT / ".tmp" / "workspace")
    with pytest.raises(SystemExit, match="refusing workspace"):
        serve_harness.check_workspace(Path.home() / "some-owner-workspace")
    with pytest.raises(SystemExit, match="refusing workspace"):
        serve_harness.check_workspace(ROOT / ".tmp" / "hci" / ".." / ".." / "workspace")  # traversal out of .tmp
    inside = serve_harness.check_workspace(ROOT / ".tmp" / "hci" / "x" / "workspace")
    assert inside.is_relative_to((ROOT / ".tmp" / "hci").resolve())


def test_harness_launcher_rejects_a_foreign_workspace_end_to_end(tmp_path):
    proc = subprocess.run(  # noqa: S603 - fixed argv
        [sys.executable, "-m", "quality.hci.serve_harness", "--workspace", str(tmp_path / "ws"), "--port", "1"],
        capture_output=True, text=True, cwd=ROOT, timeout=120, check=False,
    )
    assert proc.returncode != 0 and "refusing workspace" in proc.stderr
    assert not (tmp_path / "ws").exists()  # nothing was created there


def test_unknown_identity_is_rejected_and_release_uses_the_real_cli():
    with pytest.raises(ValueError, match="identity must be one of"), server.studio_server("x", identity="owner"):
        pytest.fail("an unknown identity must never start a server")
    argv = server._command("release", Path("w"), 1)
    assert argv[1:5] == ["-m", "eija_studio", "serve", "--provider"] and "serve_harness" not in " ".join(argv)
    assert "quality.hci.serve_harness" in server._command("harness", Path("w"), 1)
