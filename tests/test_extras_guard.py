"""A test skipped for a missing extra is named, and fails the run under EIJA_REQUIRE_EXTRAS=1 (integration review I1)."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
from extras_guard import missing_extra

TESTS = Path(__file__).resolve().parent


@pytest.mark.parametrize(("reason", "what"), [
    ("could not import 'z3': No module named 'z3'", "z3"),
    ("could not import 'verification.smt.differential': No module named 'z3'", "z3"),
    ("z3-solver is in the `smt` extra; without it the proof is NOT_RUN, not passed", "smt"),
    ("z3-solver (extra `smt`) is not installed: NOT_RUN", "smt"),
    ("NOT_RUN: install the hci or demos extra", "demos"),
    ("NOT_RUN: import-linter is in the `lint` extra", "lint"),
    ("NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1", None),
    ("NOT_RUN: Node is not installed", None),
])
def test_a_skip_reason_is_read_as_a_missing_extra_or_not(reason, what):
    assert missing_extra(reason) == what


def _run(tmp_path: Path, require: str | None) -> subprocess.CompletedProcess[str]:
    (tmp_path / "conftest.py").write_text('pytest_plugins = ["extras_guard"]\n', encoding="utf-8")
    (tmp_path / "test_sample.py").write_text(
        "import pytest\n"
        "def test_passes():\n    assert True\n"
        "def test_needs_a_module_nobody_has():\n    pytest.importorskip('eija_no_such_module_for_this_test')\n"
        "@pytest.mark.skipif(True, reason='NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1')\n"
        "def test_opt_in():\n    pass\n", encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k != "EIJA_REQUIRE_EXTRAS"}
    env["PYTHONPATH"] = os.pathsep.join([str(TESTS), env.get("PYTHONPATH", "")])
    if require is not None:
        env["EIJA_REQUIRE_EXTRAS"] = require
    command = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-p", "no:randomly", str(tmp_path)]
    return subprocess.run(command, capture_output=True, text=True, env=env, cwd=tmp_path, timeout=120, check=False)  # noqa: S603


def test_a_missing_extra_is_named_but_passes_by_default(tmp_path):
    done = _run(tmp_path, None)
    assert done.returncode == 0, done.stdout
    assert "NOT_RUN for a missing extra" in done.stdout
    assert "eija_no_such_module_for_this_test (1)" in done.stdout  # the opt-in browser skip is not counted


def test_a_missing_extra_fails_the_run_when_extras_are_required(tmp_path):
    done = _run(tmp_path, "1")
    assert done.returncode == 1, done.stdout


def test_nothing_is_listed_when_nothing_was_skipped_for_an_extra(tmp_path):
    (tmp_path / "conftest.py").write_text('pytest_plugins = ["extras_guard"]\n', encoding="utf-8")
    (tmp_path / "test_ok.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    env = dict(os.environ, EIJA_REQUIRE_EXTRAS="1", PYTHONPATH=str(TESTS))
    done = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(tmp_path)],  # noqa: S603
                          capture_output=True, text=True, env=env, cwd=tmp_path, timeout=120, check=False)
    assert done.returncode == 0 and "missing extra" not in done.stdout
