"""Tests for the quality gates themselves: a gate that cannot fail is not a gate (negative controls)."""

import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # `quality/` is engineering tooling at the repo root, not an installed package

from quality.gates import complexity_ratchet as ratchet  # noqa: E402

LINT_IMPORTS = "from importlinter.cli import lint_imports_command; lint_imports_command()"


def test_recorded_complexity_debt_matches_the_code():
    """The checked-in baseline is current: nothing grew, nothing improved without tightening, nothing vanished."""
    assert ratchet.evaluate(ratchet.measure(), ratchet.load_baseline()) == []


def test_ratchet_rejects_new_offender_and_growth_but_accepts_recorded_debt():
    measured = {"a.py::old": 30, "a.py::fresh": 11, "a.py::ok": 10}
    assert ratchet.evaluate(measured, {"a.py::old": 30}) == [
        "a.py::fresh: complexity 11 exceeds the budget of 10 (allowed 10)"
    ]
    grown = ratchet.evaluate({"a.py::old": 31}, {"a.py::old": 30})
    assert len(grown) == 1 and "grew beyond its recorded debt" in grown[0]


def test_ratchet_forces_tightening_and_removal_of_stale_debt():
    improved = ratchet.evaluate({"a.py::f": 12}, {"a.py::f": 30})
    assert len(improved) == 1 and "tighten" in improved[0]
    stale = ratchet.evaluate({}, {"a.py::gone": 30})
    assert len(stale) == 1 and "no longer exists" in stale[0]


def test_update_can_only_lower_debt_never_record_new_debt():
    measured = {"a.py::old": 12, "a.py::resolved": 9, "a.py::brand_new": 50}
    debt = {"a.py::old": 30, "a.py::resolved": 20, "a.py::vanished": 15}
    assert ratchet.tightened(measured, debt) == {"a.py::old": 12}


def test_measure_counts_branches_in_methods_and_nested_functions(tmp_path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "m.py").write_text(
        textwrap.dedent(
            """
            def flat():
                return 1

            class K:
                def branchy(self, x):
                    if x > 1:
                        return 1
                    elif x > 0:
                        return 2
                    for _ in range(x):
                        if x:
                            return 3
                    return 0
            """
        ),
        encoding="utf-8",
    )
    measured = ratchet.measure(("pkg",), base=tmp_path)
    assert measured == {"pkg/m.py::flat": 1, "pkg/m.py::K.branchy": 5}


def _run_lint_imports(workdir: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ | {"PYTHONPATH": str(workdir), "TMP": str(ROOT / ".tmp"), "TEMP": str(ROOT / ".tmp")}
    return subprocess.run(
        [sys.executable, "-c", LINT_IMPORTS],
        cwd=workdir,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def _copy_kernel(target: Path) -> Path:
    shutil.copytree(
        ROOT / "src" / "eija_studio",
        target / "eija_studio",
        ignore=shutil.ignore_patterns("__pycache__", "web"),
    )
    shutil.copy(ROOT / "pyproject.toml", target / "pyproject.toml")
    return target / "eija_studio"


def test_architecture_contracts_hold_on_a_clean_copy_and_break_on_seeded_violations(tmp_path):
    pytest.importorskip("importlinter", reason="NOT_RUN: import-linter is in the `lint` extra")
    clean = tmp_path / "clean"
    clean.mkdir()
    _copy_kernel(clean)
    ok = _run_lint_imports(clean)
    assert ok.returncode == 0, ok.stdout + ok.stderr
    assert "Contracts: 3 kept, 0 broken." in ok.stdout

    bad = tmp_path / "bad"
    bad.mkdir()
    pkg = _copy_kernel(bad)
    with (pkg / "domain" / "impact.py").open("a", encoding="utf-8", newline="\n") as f:
        f.write("import sqlite3\nimport subprocess\n")
    with (pkg / "application" / "runtime.py").open("a", encoding="utf-8", newline="\n") as f:
        f.write("from eija_studio.adapters import receipts\n")
    with (pkg / "interfaces" / "http.py").open("a", encoding="utf-8", newline="\n") as f:
        f.write("from eija_studio.adapters import receipts\n")
    broken = _run_lint_imports(bad)
    assert broken.returncode != 0
    out = broken.stdout
    assert "Contracts: 0 kept, 3 broken." in out
    assert "eija_studio.domain is not allowed to import sqlite3" in out
    assert "eija_studio.domain is not allowed to import subprocess" in out
    assert "eija_studio.application is not allowed to import eija_studio.adapters" in out
    assert "eija_studio.interfaces is not allowed to import eija_studio.adapters" in out


SH = shutil.which("sh")
needs_sh = pytest.mark.skipif(SH is None, reason="NOT_RUN: no POSIX sh on PATH")


def _hook(script: str, stdin: str | None = None, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [SH, str(ROOT / script), *args], input=stdin, capture_output=True, text=True, check=False, cwd=ROOT
    )


@needs_sh
@pytest.mark.parametrize(
    ("subject", "accepted"),
    [
        ("feat(quality): add a gate", True),
        ("chore: tidy", True),
        ("Merge pull request #7 from 45ck/lane/quality", True),
        ('Revert "feat: x"', True),
        ("added some stuff", False),
        ("chore: tidy [skip ci]", False),
    ],
)
def test_commit_msg_hook_enforces_conventional_commits(tmp_path, subject, accepted):
    message = tmp_path / "MSG"
    message.write_text(subject + "\n\nCo-Authored-By: Someone <a@b.c>\n", encoding="utf-8", newline="\n")
    assert (_hook(".githooks/commit-msg", None, str(message)).returncode == 0) is accepted


@needs_sh
def test_claude_guardrail_hook_blocks_gate_bypass_and_allows_normal_commands():
    bypass_flag = "--no" + "-verify"  # assembled so this file does not itself contain the blocked text
    blocked = _hook(
        ".claude/hooks/pre-tool-use.sh", '{"tool_input":{"command":"git commit ' + bypass_flag + '"}}'
    )
    assert blocked.returncode == 2 and "bypass" in blocked.stderr
    allowed = _hook(".claude/hooks/pre-tool-use.sh", '{"tool_input":{"command":"git status"}}')
    assert allowed.returncode == 0
