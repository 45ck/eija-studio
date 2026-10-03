"""Process-boundary controls independent of native syntax fixture tests."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from eija_studio.adapters import repository_analysis as adapter
from eija_studio.weave import extract_javascript


@pytest.mark.parametrize(
    "error,reason",
    [
        (adapter.CliTimeout(), "PARSER_TIMEOUT"),
        (adapter.CliOutputLimit(), "PARSER_OUTPUT_LIMIT"),
        (OSError(), "PARSER_UNAVAILABLE"),
    ],
)
def test_runner_failures_are_not_run_and_do_not_escape(monkeypatch, error, reason):
    def fail(*args, **kwargs):
        raise error

    monkeypatch.setattr(adapter, "run_bounded", fail)
    result = adapter.syntax_reader("a.js", b"function f(){}")
    assert result["status"] == "NOT_RUN"
    assert result["gaps"][0]["reason"] == reason
    assert not result["symbols"]


@pytest.mark.parametrize(
    "returncode,stdout,reason",
    [
        (-1073741819, "", "PARSER_PROCESS_FAILED"),
        (0, "not JSON", "PARSER_RESPONSE_INVALID"),
        (0, "[]", "PARSER_RESPONSE_INVALID"),
        (0, '{"status":"PASS"}', "PARSER_RESPONSE_INVALID"),
    ],
)
def test_crash_and_invalid_output_do_not_become_extracted(monkeypatch, returncode, stdout, reason):
    monkeypatch.setattr(
        adapter,
        "run_bounded",
        lambda *a, **k: subprocess.CompletedProcess([], returncode, stdout, "private-error"),
    )
    result = adapter.syntax_reader("a.js", b"function f(){}")
    assert result["status"] == "NOT_RUN"
    assert result["gaps"][0]["reason"] == reason
    assert "private-error" not in str(result)


def test_worker_uses_fixed_script_stdin_and_minimal_environment(monkeypatch):
    seen = {}

    def runner(args, **kwargs):
        seen.update(args=args, **kwargs)
        return subprocess.CompletedProcess(
            args,
            0,
            json.dumps(
                {
                    "status": "EXTRACTED",
                    "method": extract_javascript.METHOD,
                    "symbols": [],
                    "gaps": [],
                }
            ),
            "",
        )

    monkeypatch.setenv("PROVIDER_SECRET", "test-must-not-cross")
    monkeypatch.setattr(adapter, "run_bounded", runner)
    result = adapter.syntax_reader("some/target.js", b"function f(){}")
    assert result["status"] == "EXTRACTED"
    assert seen["args"][1:3] == ["-I", "-B"]
    assert seen["args"][-1] == "--worker"
    assert Path(seen["args"][3]) == Path(extract_javascript.__file__).resolve()
    assert "some/target.js" not in seen["args"]
    assert "PROVIDER_SECRET" not in seen["env"]
    assert set(seen["env"]) <= {"SYSTEMROOT", "WINDIR", "SystemRoot", "windir"}
    assert seen["timeout"] == 10.0
    assert seen["max_bytes"] == 8 * 1024 * 1024


def test_real_child_parse_or_explicit_missing_dependency():
    result = adapter.syntax_reader("a.js", b"function actual(){return 7}")
    try:
        extract_javascript._load_parser()
    except (ImportError, ValueError, OSError):
        assert result["status"] == "NOT_RUN"
        pytest.skip("NOT_RUN: pinned JavaScript parser unavailable")
    assert result["status"] == "EXTRACTED"
    assert result["symbols"][0]["reference"] == "repo://a.js#js/function/actual"


@pytest.mark.parametrize(
    "program,timeout,reason",
    [
        ("import os\nos._exit(37)\n", 2.0, "PARSER_PROCESS_FAILED"),
        ("import time\ntime.sleep(30)\n", 0.1, "PARSER_TIMEOUT"),
    ],
)
def test_actual_abrupt_child_exit_and_timeout_are_contained(monkeypatch, tmp_path, program, timeout, reason):
    worker = tmp_path / "controlled_worker.py"
    worker.write_text(program, encoding="utf-8", newline="\n")
    monkeypatch.setattr(extract_javascript, "__file__", str(worker))
    monkeypatch.setattr(adapter, "TIMEOUT_SECONDS", timeout)
    result = adapter.syntax_reader("a.js", b"function f(){}")
    assert result["status"] == "NOT_RUN"
    assert result["gaps"][0]["reason"] == reason
