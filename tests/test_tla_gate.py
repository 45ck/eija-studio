"""The TLA gate must observe this invocation, including a real failed child process."""
import json
import sys

import nox.command
import pytest

from quality.sessions import tla
from verification.tla import run


class GateStop(RuntimeError):
    pass


class ChildSession:
    """Keep nox's actual exit-code handling; substitute a tiny child for costly TLC."""

    def __init__(self, report, payload=None, code=0, posargs=()):
        self.report, self.payload, self.code = report, payload, code
        self.posargs, self.logs, self.commands = list(posargs), [], []

    def run(self, *args, **kwargs):
        self.commands.append(args)
        script = "from pathlib import Path; import sys\n"
        if self.payload is not None:
            script += f"Path({str(self.report)!r}).write_text({self.payload!r}, encoding='utf-8')\n"
        script += f"sys.exit({self.code})\n"
        return nox.command.run([sys.executable, "-c", script], silent=True, log=False, **kwargs)

    def error(self, reason):
        raise GateStop("FAIL: " + reason)

    def skip(self, reason):
        raise GateStop("SKIP: " + reason)

    def log(self, message):
        self.logs.append(message)


@pytest.fixture
def report(tmp_path, monkeypatch):
    path = tmp_path / "tla.json"
    monkeypatch.setattr(tla, "REPORT", path)
    return path


@pytest.mark.parametrize("code", [1, 2])
def test_failed_child_cannot_reuse_a_prior_pass(report, code):
    previous = '{"result":"PASS","created_at":"prior-run"}'
    report.write_text(previous, encoding="utf-8")
    session = ChildSession(report, code=code)
    with pytest.raises(nox.command.CommandFailed):
        tla._run(session)
    assert json.loads(report.read_text(encoding="utf-8"))["result"] == "FAIL"
    assert [path.read_text(encoding="utf-8") for path in report.parent.glob("tla.previous-*.json")] == [previous]
    assert not any("formal_tla PASS" in message for message in session.logs)


def test_zero_exit_without_a_fresh_report_cannot_reuse_a_prior_pass(report):
    report.write_text('{"result":"PASS"}', encoding="utf-8")
    with pytest.raises(GateStop, match="no readable current report"):
        tla._run(ChildSession(report))


@pytest.mark.parametrize("payload", ["not json", "[]", "{}", '{"result":"UNKNOWN"}', '{"result":"FAIL"}'])
def test_zero_exit_invalid_or_failed_current_report_fails(report, payload):
    with pytest.raises(GateStop, match="FAIL"):
        tla._run(ChildSession(report, payload))


@pytest.mark.parametrize("code", [1, 2])
@pytest.mark.parametrize("result", ["PASS", "NOT_RUN"])
def test_fresh_report_cannot_override_failed_child_exit(report, code, result):
    with pytest.raises(nox.command.CommandFailed):
        tla._run(ChildSession(report, json.dumps({"result": result}), code))
    assert json.loads(report.read_text(encoding="utf-8"))["result"] == "FAIL"
    assert [json.loads(path.read_text(encoding="utf-8"))["result"]
            for path in report.parent.glob("tla.previous-*.json")] == [result]


def test_fresh_not_run_is_a_skip_and_never_a_pass(report):
    session = ChildSession(report, '{"result":"NOT_RUN","reason":"Java unavailable"}')
    with pytest.raises(GateStop, match="SKIP: NOT_RUN: Java unavailable"):
        tla._run(session)
    assert not any("formal_tla PASS" in message for message in session.logs)


def test_fresh_success_pins_the_current_report_and_full_configuration_set(report):
    session = ChildSession(report, '{"result":"PASS"}')
    tla._run(session)
    assert session.commands[0][-4:] == ("--out", str(report), "--configs", "")
    assert session.logs == [f"formal_tla PASS: {report}"]


@pytest.mark.parametrize("args", [("--out", "elsewhere.json"), ("--out=elsewhere.json",),
                                 ("--configs", "baseline"), ("--configs=baseline",)])
def test_required_gate_rejects_output_and_coverage_overrides(report, args):
    session = ChildSession(report, posargs=args)
    with pytest.raises(GateStop, match="complete configuration set"):
        tla._run(session)
    assert session.commands == []


@pytest.mark.parametrize("selection", ["typo", "baseline,typo", ",", "  "])
def test_unknown_or_empty_configuration_selection_cannot_vacuously_pass(tmp_path, selection):
    report = tmp_path / "tla.json"
    with pytest.raises(SystemExit) as failed:
        run.main(["--configs", selection, "--out", str(report), "--no-fetch"])
    assert failed.value.code == 2
    assert not report.exists()
