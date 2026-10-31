"""Lane sessions skip their own pytest files only when the suite session of the same nox run covers them (quality/tools/suite.py)."""
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

from quality.tools import suite

ROOT = Path(__file__).resolve().parents[2]

# A lane whose own test file fails: if the lane skips it, only the suite session in the same run can have covered it.
NOXFILE = f'''
import sys
sys.path.insert(0, {str(ROOT)!r})
import nox
from quality.tools.suite import run_lane_tests

@nox.session(python=False, tags=["tier"])
def tests(session):
    session.log("suite ran")

@nox.session(python=False, tags=["tier"])
def lane(session):
    run_lane_tests(session, "-p", "no:cacheprovider", "test_planted.py")
'''
PLANTED = "def test_planted_defect():\n    assert 1 == 2  # planted: a lane run on its own must still fail on this\n"


def _session(*names: str, consumed: tuple[str, ...] = ()) -> SimpleNamespace:
    runner = lambda name: SimpleNamespace(name=name)  # noqa: E731
    manifest = SimpleNamespace(_consumed=[runner(n) for n in consumed], _queue=[runner(n) for n in names])
    return SimpleNamespace(_runner=SimpleNamespace(manifest=manifest))


def test_a_suite_session_queued_or_already_run_counts_as_selected():
    assert suite.suite_selected(_session("vocabulary", "tests"))
    assert suite.suite_selected(_session("vocabulary", consumed=("coverage",)))
    assert not suite.suite_selected(_session("vocabulary", "lint"))


def test_an_unknown_nox_shape_means_the_lane_runs_its_own_tests():
    assert not suite.suite_selected(SimpleNamespace())


def _nox(tmp_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    (tmp_path / "noxfile.py").write_text(NOXFILE, encoding="utf-8")
    (tmp_path / "test_planted.py").write_text(PLANTED, encoding="utf-8")
    argv = [sys.executable, "-m", "nox", "-f", str(tmp_path / "noxfile.py"), *args]
    return subprocess.run(argv, cwd=tmp_path, capture_output=True, text=True, check=False, timeout=120)  # noqa: S603 - fixed interpreter, test-owned noxfile


def test_the_lane_alone_still_runs_and_fails_on_its_own_tests(tmp_path):
    result = _nox(tmp_path, "-s", "lane")
    assert result.returncode != 0, result.stdout + result.stderr
    assert "test_planted_defect" in result.stdout + result.stderr


def test_in_a_tier_with_the_suite_session_the_lane_leaves_its_files_to_it(tmp_path):
    result = _nox(tmp_path, "-t", "tier")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "run by the suite session in this run" in result.stderr


def test_the_old_behaviour_is_one_environment_variable_away(tmp_path, monkeypatch):
    monkeypatch.setenv("EIJA_LANE_TESTS", "always")
    assert _nox(tmp_path, "-t", "tier").returncode != 0
