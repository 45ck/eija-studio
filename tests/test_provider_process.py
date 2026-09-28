"""Real-process tests for the bounded runner. No vendor CLI and no network: only the Python interpreter."""
import json
import os
import sys
import time
from pathlib import Path

import pytest

from eija_studio.adapters.providers import process
from eija_studio.adapters.providers.cli_base import BASE_ENV_ALLOW, build_environment
from eija_studio.adapters.providers.process import CliOutputLimit, CliShimUnsupported, CliTimeout, run_bounded

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
    monkeypatch.setattr(process.shutil, "which", lambda name: "C:/fake/node.exe" if name == "node" else None)
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
