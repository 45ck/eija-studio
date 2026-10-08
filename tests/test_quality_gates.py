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

LINT_IMPORTS = "from importlinter.cli import lint_imports_command; lint_imports_command()"


@pytest.fixture(scope="module")
def ratchet():
    """The ratchet needs radon (the `lint` extra). With only `.[dev]` installed the tests skip: NOT_RUN, not error."""
    pytest.importorskip(
        "radon", reason="NOT_RUN: radon is in the `lint` extra (pip install -e '.[dev,lint]')"
    )
    from quality.gates import complexity_ratchet

    return complexity_ratchet


def test_recorded_complexity_debt_matches_the_code(ratchet):
    """The checked-in baseline is current: nothing grew, nothing improved without tightening, nothing vanished."""
    assert ratchet.evaluate(ratchet.measure(), ratchet.load_baseline()) == []


def test_ratchet_rejects_new_offender_and_growth_but_accepts_recorded_debt(ratchet):
    measured = {"a.py::old": 30, "a.py::fresh": 11, "a.py::ok": 10}
    assert ratchet.evaluate(measured, {"a.py::old": 30}) == [
        "a.py::fresh: complexity 11 exceeds the budget of 10 (allowed 10)"
    ]
    grown = ratchet.evaluate({"a.py::old": 31}, {"a.py::old": 30})
    assert len(grown) == 1 and "grew beyond its recorded debt" in grown[0]


def test_ratchet_forces_tightening_and_removal_of_stale_debt(ratchet):
    improved = ratchet.evaluate({"a.py::f": 12}, {"a.py::f": 30})
    assert len(improved) == 1 and "tighten" in improved[0]
    stale = ratchet.evaluate({}, {"a.py::gone": 30})
    assert len(stale) == 1 and "no longer exists" in stale[0]


def test_update_can_only_lower_debt_never_record_new_debt(ratchet):
    measured = {"a.py::old": 12, "a.py::resolved": 9, "a.py::brand_new": 50}
    debt = {"a.py::old": 30, "a.py::resolved": 20, "a.py::vanished": 15}
    assert ratchet.tightened(measured, debt) == {"a.py::old": 12}


def test_update_never_launders_growth_of_recorded_debt(ratchet):
    """Negative control: a function that got WORSE keeps its old pin, so the check still fails after --update."""
    measured, debt = {"a.py::old": 31}, {"a.py::old": 30}
    assert ratchet.tightened(measured, debt) == {"a.py::old": 30}
    assert ratchet.evaluate(measured, ratchet.tightened(measured, debt)) != []


def test_measure_counts_branches_in_methods_and_nested_functions(ratchet, tmp_path):
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


def test_measure_reaches_methods_of_nested_classes_and_skips_missing_roots(ratchet, tmp_path):
    (tmp_path / "pkg").mkdir()
    body = "".join(f"            if x == {i}:\n                return {i}\n" for i in range(12))
    source = "class Outer:\n    class Inner:\n        def f(self, x):\n" + body
    (tmp_path / "pkg" / "m.py").write_text(source, encoding="utf-8", newline="\n")
    measured = ratchet.measure(("pkg", "absent-root"), base=tmp_path)
    assert measured == {"pkg/m.py::Outer.Inner.f": 13}
    assert ratchet.evaluate(measured, {}) != []


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


def test_network_stdlib_in_application_and_an_unlayered_subpackage_are_caught(tmp_path):
    """Negative controls for the two gaps a reviewer found: stdlib network access, and a package with no layer."""
    pytest.importorskip("importlinter", reason="NOT_RUN: import-linter is in the `lint` extra")
    net = tmp_path / "net"
    net.mkdir()
    pkg = _copy_kernel(net)
    with (pkg / "application" / "runtime.py").open("a", encoding="utf-8", newline="\n") as f:
        f.write("import urllib.request\nimport socket\n")
    out = _run_lint_imports(net).stdout
    assert "Contracts: 2 kept, 1 broken." in out
    assert "eija_studio.application is not allowed to import urllib" in out
    assert "eija_studio.application is not allowed to import socket" in out

    unlayered = tmp_path / "unlayered"
    unlayered.mkdir()
    pkg = _copy_kernel(unlayered)
    (pkg / "newlane").mkdir()
    (pkg / "newlane" / "__init__.py").write_bytes(b"")
    result = _run_lint_imports(unlayered)
    assert result.returncode != 0
    assert "newlane" in result.stdout


class _FakeSession:
    """Just enough of nox.Session to observe how the audit gate reports a missing network."""

    posargs: list[str] = []  # noqa: RUF012

    def __init__(self):
        self.outcome = None

    def skip(self, reason):
        self.outcome = ("skip", reason)
        raise RuntimeError("skip")

    def error(self, reason):
        self.outcome = ("error", reason)
        raise RuntimeError("error")

    def run(self, *args, **kwargs):
        self.outcome = ("ran", args)


def test_audit_gate_fails_offline_unless_the_gap_is_explicitly_accepted(monkeypatch, capsys):
    """NOT_RUN must not exit 0 by accident: nox reads a skipped session as success."""
    nox = pytest.importorskip("nox", reason="NOT_RUN: nox is in the `dev` extra")
    assert nox
    from quality.sessions import quality as sessions

    monkeypatch.setattr(sessions, "_pypi_reachable", lambda: False)
    monkeypatch.delenv("EIJA_ALLOW_NOT_RUN", raising=False)
    session = _FakeSession()
    with pytest.raises(RuntimeError, match="error"):
        sessions.audit.func(session)
    assert session.outcome[0] == "error" and "NOT_RUN" in session.outcome[1]

    monkeypatch.setenv("EIJA_ALLOW_NOT_RUN", "1")
    session = _FakeSession()
    with pytest.raises(RuntimeError, match="skip"):
        sessions.audit.func(session)
    assert session.outcome[0] == "skip" and "NOT_RUN" in capsys.readouterr().out


def _tool(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ | {"TMP": str(ROOT / ".tmp"), "TEMP": str(ROOT / ".tmp")}
    return subprocess.run(
        [sys.executable, "-m", *args], cwd=cwd, env=env, capture_output=True, text=True, check=False
    )


def test_ruff_flags_a_shell_true_call_in_the_domain(tmp_path):
    """Negative control: the bandit subset is active for kernel code, so `shell=True` cannot land quietly."""
    pytest.importorskip("ruff", reason="NOT_RUN: ruff is in the `lint` extra")
    shutil.copy(ROOT / "pyproject.toml", tmp_path / "pyproject.toml")
    domain = tmp_path / "src" / "eija_studio" / "domain"
    domain.mkdir(parents=True)
    (domain / "bad.py").write_bytes(
        b"import subprocess\n\n\ndef run(cmd: str) -> None:\n    subprocess.run(cmd, shell=True)\n"
    )
    result = _tool("ruff", "check", "--no-cache", "src", cwd=tmp_path)
    assert result.returncode != 0 and "S602" in result.stdout, result.stdout + result.stderr


def test_mypy_strict_rejects_an_untyped_def_and_an_untyped_optional_return_in_the_domain(tmp_path):
    """Negative control: `disallow_untyped_defs` and `no_implicit_optional` are live on `eija_studio.domain`."""
    pytest.importorskip("mypy", reason="NOT_RUN: mypy is in the `lint` extra")
    shutil.copy(ROOT / "pyproject.toml", tmp_path / "pyproject.toml")
    domain = tmp_path / "src" / "eija_studio" / "domain"
    domain.mkdir(parents=True)
    (tmp_path / "src" / "eija_studio" / "__init__.py").write_bytes(b"")
    (domain / "__init__.py").write_bytes(b"")
    (domain / "bad.py").write_bytes(
        b"def untyped(x):\n    return x\n\n\ndef opt(x: int = None) -> int:\n    return x\n"
    )
    result = _tool("mypy", "--no-incremental", cwd=tmp_path)
    assert result.returncode != 0, result.stdout
    assert "no-untyped-def" in result.stdout and "assignment" in result.stdout, result.stdout


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


def _guard(command: str) -> subprocess.CompletedProcess[str]:
    payload = '{"tool_input":{"command":"' + command.replace('"', '\\"') + '"}}'
    return _hook(".claude/hooks/pre-tool-use.sh", payload)


# Assembled so this file does not itself contain the literal blocked text.
BYPASS_LONG = "--no" + "-verify"


@needs_sh
@pytest.mark.parametrize(
    "command",
    [
        f"git commit {BYPASS_LONG} -m x",
        "git commit -n -m x",
        "git commit -nm x",
        "git commit -anm x",
        "git -c core.hooksPath=/dev/null commit -m x",
        "HUSKY=0 git commit -m x",
        "git commit -m 'chore: tidy [skip ci]'",
    ],
)
def test_claude_guardrail_hook_blocks_gate_bypass_forms(command):
    blocked = _guard(command)
    assert blocked.returncode == 2 and blocked.stderr.startswith("noslop:"), command


@needs_sh
@pytest.mark.parametrize(
    "command",
    [
        "git status",
        'git commit -m "feat(quality): add a gate"',
        "git commit -am wip",
        "git commit --amend --no-edit",
        "git worktree remove --force ../wt",
        "git push --force-with-lease origin lane/quality",
    ],
)
def test_claude_guardrail_hook_allows_normal_commands(command):
    assert _guard(command).returncode == 0, command
