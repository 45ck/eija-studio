"""CLI behaviours that need neither a browser nor a server: file moves, exit codes, no stray output."""
import importlib.util
from types import SimpleNamespace

import pytest

from demos import __main__ as cli
from demos.lib import BrowserUnavailableError, Recorder


def test_move_replacing_overwrites_an_existing_destination(tmp_path):
    source, destination = tmp_path / "take.webm", tmp_path / "final.webm"
    source.write_bytes(b"new")
    destination.write_bytes(b"old")
    cli._move_replacing(source, destination)
    assert destination.read_bytes() == b"new" and not source.exists()


def test_move_replacing_retries_a_transient_permission_error(tmp_path, monkeypatch):
    source, destination = tmp_path / "take.webm", tmp_path / "final.webm"
    source.write_bytes(b"new")
    real_replace = type(source).replace
    calls = {"n": 0}

    def flaky(self, target):
        calls["n"] += 1
        if calls["n"] < 3:
            raise PermissionError("WinError 32: file in use")
        return real_replace(self, target)

    monkeypatch.setattr(type(source), "replace", flaky)
    cli._move_replacing(source, destination, delay_s=0)
    assert calls["n"] == 3 and destination.read_bytes() == b"new"


def test_move_replacing_gives_up_after_the_attempt_budget(tmp_path, monkeypatch):
    source, destination = tmp_path / "take.webm", tmp_path / "final.webm"
    source.write_bytes(b"new")

    def locked(self, target):
        raise PermissionError("locked")

    monkeypatch.setattr(type(source), "replace", locked)
    with pytest.raises(PermissionError):
        cli._move_replacing(source, destination, attempts=3, delay_s=0)


def test_unknown_scenario_is_a_usage_error(capsys):
    assert cli.main(["run", "no_such_scenario", "--dry-run"]) == cli.EXIT_USAGE


def test_blocked_scenario_is_not_run_and_names_the_lane_it_waits_for(capsys):
    assert cli.main(["run", "uml_drag_and_drop", "--dry-run"]) == cli.EXIT_NOT_RUN
    out = capsys.readouterr().out
    assert out.startswith("NOT_RUN") and "blocked on lane(s) uml-editor" in out and "visual" not in out


def test_unscripted_scenario_is_not_run_and_says_there_is_no_script(capsys):
    assert cli.main(["run", "visual_diff_and_ripple", "--dry-run"]) == cli.EXIT_NOT_RUN
    out = capsys.readouterr().out
    assert out.startswith("NOT_RUN") and "no scenario script exists yet" in out and "blocked on" not in out


def test_missing_playwright_is_not_run_not_a_pass(capsys, monkeypatch):
    real = importlib.util.find_spec
    monkeypatch.setattr(importlib.util, "find_spec", lambda name, *a: None if name == "playwright" else real(name, *a))
    assert cli.main(["run", "assurance_loop", "--dry-run"]) == cli.EXIT_NOT_RUN
    assert "NOT_RUN" in capsys.readouterr().out


def test_seed_help_does_not_promise_repeatable_recordings(capsys):
    with pytest.raises(SystemExit):
        cli.main(["run", "--help"])
    help_text = " ".join(capsys.readouterr().out.split())
    assert "typing cadence ONLY" in help_text and "recordings are repeatable" not in help_text


@pytest.fixture
def playwright_found(monkeypatch):
    """Make the preflight believe Playwright is installed, so `_run` reaches `_execute` (which the test fakes)."""
    real = importlib.util.find_spec
    monkeypatch.setattr(importlib.util, "find_spec", lambda name, *a: object() if name == "playwright" else real(name, *a))


def test_browser_launch_failure_maps_to_not_run(playwright_found, monkeypatch, capsys):
    def no_browser(*args, **kwargs):
        raise BrowserUnavailableError("could not launch the system Chrome: not installed")

    monkeypatch.setattr(cli, "_execute", no_browser)
    assert cli.main(["run", "assurance_loop", "--dry-run"]) == cli.EXIT_NOT_RUN
    assert capsys.readouterr().out.startswith("NOT_RUN")


def test_scenario_errors_are_failures_not_not_run(playwright_found, monkeypatch):
    def broken(*args, **kwargs):
        raise RuntimeError("the Studio no longer has this control")

    monkeypatch.setattr(cli, "_execute", broken)
    with pytest.raises(RuntimeError):
        cli.main(["run", "assurance_loop", "--dry-run"])


def test_partial_prints_a_clear_line_and_exits_zero(playwright_found, monkeypatch, capsys):
    monkeypatch.setattr(cli, "_execute", lambda *a, **k: (["Act 4 skipped"], None))
    assert cli.main(["run", "assurance_loop", "--dry-run"]) == 0
    out = capsys.readouterr().out
    assert "PARTIAL assurance_loop: 1 act(s) not exercised" in out and "Act 4 skipped" in out


def test_full_pass_prints_pass(playwright_found, monkeypatch, capsys):
    monkeypatch.setattr(cli, "_execute", lambda *a, **k: ([], None))
    assert cli.main(["run", "assurance_loop", "--dry-run"]) == 0
    assert "PASS assurance_loop" in capsys.readouterr().out


def test_launch_failure_raises_browser_unavailable_and_writes_nothing(monkeypatch, tmp_path):
    sync_api = pytest.importorskip("playwright.sync_api")

    class FakePlaywright:
        chromium = SimpleNamespace(launch=lambda **kw: (_ for _ in ()).throw(sync_api.Error("no chrome")))

    class FakeContext:
        def __enter__(self):
            return FakePlaywright()

        def __exit__(self, *exc):
            return False

    monkeypatch.setattr(sync_api, "sync_playwright", FakeContext)
    out_dir = tmp_path / "take"
    with pytest.raises(BrowserUnavailableError), Recorder().session(out_dir, dry_run=True):
        pass
    assert not out_dir.exists()
