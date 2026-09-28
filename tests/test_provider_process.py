"""Real-process tests for the bounded runner. No vendor CLI and no network: only the Python interpreter."""
import json
import os
import sys
import threading
import time
from pathlib import Path

import pytest

from eija_studio.adapters.providers import OfflineProvider, process
from eija_studio.adapters.providers.cli_base import BASE_ENV_ALLOW, CliProposalProvider, Extracted, Invocation, LoginState, build_environment
from eija_studio.adapters.providers.process import CliOutputLimit, CliShimUnsupported, CliTimeout, run_bounded
from eija_studio.domain.policy import baseline

PY = sys.executable
ENV = {k: v for k, v in os.environ.items() if k.upper() in {"PATH", "SYSTEMROOT", "TEMP", "TMP"}}

HEARTBEAT = """
import os, subprocess, sys, time
beat = sys.argv[1]
child = "import sys,time\\nwhile True:\\n    open(sys.argv[1],'a').write('x')\\n    time.sleep(0.05)\\n"
subprocess.Popen([sys.executable, "-c", child, beat])
print("started", flush=True)
time.sleep(int(sys.argv[2]))
"""


# The parent exits within milliseconds, before any periodic descendant scan could have seen the grandchild.
QUICK_PARENT = """
import subprocess, sys
child = "import sys,time\\nwhile True:\\n    open(sys.argv[1],'a').write('x')\\n    time.sleep(0.05)\\n"
subprocess.Popen([sys.executable, "-c", child, sys.argv[1]])
"""


def _alive(path: Path) -> bool:
    before = path.stat().st_size if path.exists() else 0
    time.sleep(0.6)
    return (path.stat().st_size if path.exists() else 0) > before


def test_stdin_is_delivered_and_output_captured():
    result = run_bounded([PY, "-c", "import sys; print(sys.stdin.read().upper())"], input="hello \u00e9", env=ENV | {"PYTHONIOENCODING": "utf-8"}, timeout=20)
    assert result.returncode == 0 and result.stdout.strip() == "HELLO \u00c9"


def test_nonzero_exit_and_stderr_are_returned_not_raised():
    result = run_bounded([PY, "-c", "import sys; sys.stderr.write('bad'); sys.exit(3)"], input=None, env=ENV, timeout=20)
    assert result.returncode == 3 and result.stderr == "bad"


def test_child_sees_only_the_environment_it_is_given():
    result = run_bounded([PY, "-c", "import os,json; print(json.dumps(sorted(k.upper() for k in os.environ)))"], input=None,
                         env=ENV | {"ONLY_THIS": "1"}, timeout=20)
    names = set(json.loads(result.stdout))
    assert "ONLY_THIS" in names and "HOME" not in names and "USERPROFILE" not in names


def test_output_beyond_the_cap_kills_the_process_and_raises():
    started = time.monotonic()
    with pytest.raises(CliOutputLimit):
        run_bounded([PY, "-c", "import sys\nwhile True:\n    sys.stdout.write('x'*65536); sys.stdout.flush()"], input=None, env=ENV,
                    timeout=30, max_bytes=100000)
    assert time.monotonic() - started < 20


@pytest.mark.parametrize("with_psutil", [True, False], ids=["psutil", "fallback"])
def test_timeout_kills_the_whole_process_tree(tmp_path, monkeypatch, with_psutil):
    if with_psutil and process._psutil is None:
        pytest.skip("psutil is part of the providers extra; the fallback variant still runs")
    if not with_psutil:
        monkeypatch.setattr(process, "_psutil", None)
    beat = tmp_path / "beat.txt"
    with pytest.raises(CliTimeout) as caught:
        run_bounded([PY, "-c", HEARTBEAT, str(beat), "60"], input=None, env=ENV, timeout=3)
    assert "started" in caught.value.stdout
    assert beat.exists() and beat.stat().st_size > 0, "grandchild never ran"
    assert not _alive(beat), "grandchild survived the timeout: process tree was not killed"


@pytest.mark.skipif(process._psutil is None, reason="reparented-descendant tracking needs psutil")
def test_grandchild_holding_the_pipe_after_parent_exit_is_killed(tmp_path):
    beat = tmp_path / "beat.txt"
    started = time.monotonic()
    with pytest.raises(CliTimeout):
        run_bounded([PY, "-c", HEARTBEAT, str(beat), "1"], input=None, env=ENV, timeout=4)
    assert time.monotonic() - started < 15
    assert not _alive(beat)


@pytest.mark.parametrize("with_psutil", [True, False], ids=["psutil", "fallback"])
def test_parent_exiting_at_once_cannot_hang_the_runner_or_leak_the_grandchild(tmp_path, monkeypatch, with_psutil):
    """Regression: a grandchild that outlives a very fast parent held the pipe open and run_bounded blocked forever."""
    if with_psutil and process._psutil is None:
        pytest.skip("psutil is part of the providers extra; the fallback variant still runs")
    if not with_psutil:
        monkeypatch.setattr(process, "_psutil", None)
    beat = tmp_path / "beat.txt"
    outcome: dict[str, object] = {}

    def call() -> None:
        try:
            run_bounded([PY, "-c", QUICK_PARENT, str(beat)], input=None, env=ENV, timeout=3)
            outcome["result"] = "returned"
        except CliTimeout:
            outcome["result"] = "timeout"

    worker = threading.Thread(target=call, daemon=True)
    worker.start()
    worker.join(20)
    assert not worker.is_alive(), "run_bounded blocked past its deadline"
    assert outcome["result"] == "timeout"  # the grandchild kept the pipe open: treated as a hung tree
    assert beat.exists() and beat.stat().st_size > 0, "grandchild never ran"
    assert not _alive(beat), "grandchild survived: process tree was not killed"


def test_environment_builder_drops_secret_looking_names_even_if_allowed():
    env = build_environment({"PATH": "p", "MY_TOKEN": "t", "OPENAI_API_KEY": "k", "HOME": "h"}, BASE_ENV_ALLOW | {"MY_TOKEN"})
    assert env == {"PATH": "p", "HOME": "h"}


NPM_SHIM = r'''@ECHO off
GOTO start
:find_dp0
SET dp0=%~dp0
EXIT /b
:start
SETLOCAL
CALL :find_dp0

IF EXIST "%dp0%\node.exe" (
  SET "_prog=%dp0%\node.exe"
) ELSE (
  SET "_prog=node"
  SET PATHEXT=%PATHEXT:;.JS;=;%
)

endLocal & goto #_undefined_# 2>NUL || title %COMSPEC% & "%_prog%" --no-warnings=DEP0040 "%dp0%\node_modules\pkg\bin\tool.js" %*
'''


def test_npm_cmd_shim_is_unwrapped_to_node_never_cmd_exe(tmp_path, monkeypatch):
    script = tmp_path / "node_modules" / "pkg" / "bin" / "tool.js"
    script.parent.mkdir(parents=True)
    script.write_text("//", encoding="utf-8")
    shim = tmp_path / "tool.cmd"
    shim.write_text(NPM_SHIM, encoding="utf-8")
    monkeypatch.setattr(process, "_find_executable", lambda name: "C:/fake/node.exe" if name == "node" else None)
    argv = process._unwrap_node_shim(shim)
    assert argv[0] == "C:/fake/node.exe" and argv[1] == "--no-warnings=DEP0040" and Path(argv[2]) == script
    assert not any(Path(a).name.lower() in {"cmd", "cmd.exe"} for a in argv)


def test_unrecognised_cmd_shim_is_refused_not_run_through_cmd(tmp_path):
    shim = tmp_path / "evil.cmd"
    shim.write_text("@echo off\r\ncalc.exe %*\r\n", encoding="utf-8")
    with pytest.raises(CliShimUnsupported):
        process._unwrap_node_shim(shim)


def test_missing_executable_raises_file_not_found():
    with pytest.raises(FileNotFoundError):
        process.resolve_command("eija-definitely-not-installed")


def test_executable_planted_in_the_current_directory_is_never_chosen(tmp_path, monkeypatch):
    """shutil.which prepends the current directory on Windows; resolve_command must not."""
    name = "eija-planted-cli"
    planted = tmp_path / (name + (".exe" if os.name == "nt" else ""))
    planted.write_bytes(b"MZ")
    planted.chmod(0o755)
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("NoDefaultCurrentDirectoryInExePath", raising=False)
    monkeypatch.setenv("PATH", os.pathsep.join(["", ".", "relative-dir"]))
    with pytest.raises(FileNotFoundError):
        process.resolve_command(name)
    monkeypatch.setenv("PATH", str(tmp_path))  # an ABSOLUTE PATH entry is a deliberate choice and is honoured
    assert Path(process.resolve_command(name)[0]).resolve() == planted.resolve()


FAKE_CLI = r"""
import json, os, sys
prompt = sys.stdin.read()
assert os.listdir(os.getcwd()) == [], "cwd must be an empty temp directory"
assert "sk-never" not in json.dumps(dict(os.environ)), "secret leaked into the child environment"
sys.stdout.write(open(sys.argv[1], encoding="utf-8").read() if "CANARY" in prompt else "no canary on stdin")
"""


def _fake_cli_provider(tmp_path, proposal_path):

    script = tmp_path / "fake_cli.py"
    script.write_text(FAKE_CLI, encoding="utf-8")

    class Fake(CliProposalProvider):
        name, label = "fake", "Fake CLI"
        required_flags = ("--version",)

        def login_state(self, status):
            return LoginState("LOGGED_IN")

        def invocation(self, work):
            return Invocation((str(script), str(proposal_path)))

        def extract(self, result, work):
            return Extracted(result.stdout)

    return Fake


def test_provider_runs_through_the_real_runner_resolver_stdin_and_empty_cwd(tmp_path, monkeypatch):
    """No mocked runner: real resolve_command + run_bounded + temp cwd + env allow-list + stdin, via a tiny fake CLI."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-never")
    proposal = tmp_path / "proposal.json"
    proposal.write_text(OfflineProvider().propose("Let teachers sign off excursions.", baseline()).proposal.model_dump_json(), encoding="utf-8")
    provider = _fake_cli_provider(tmp_path, proposal)(executable=sys.executable, timeout=30)
    result = provider.propose("CANARY request", baseline())
    assert result.provider == "fake" and result.live and result.proposal.alternatives
    assert result.model == "unreported"  # a CLI that reports no model is never given an invented one
