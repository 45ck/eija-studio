"""Teardown and readiness helpers of the ephemeral server: no real Studio is started."""
import subprocess
import sys
import time

import pytest

from demos.lib import server


def test_remove_tree_retries_until_windows_releases_the_handles(tmp_path, monkeypatch):
    target = tmp_path / "scratch"
    target.mkdir()
    real_rmtree, calls = server.shutil.rmtree, {"n": 0}

    def flaky(path):
        calls["n"] += 1
        if calls["n"] < 3:
            raise PermissionError("server.log is still open")
        real_rmtree(path)

    monkeypatch.setattr(server.shutil, "rmtree", flaky)
    assert server._remove_tree(target, delay_s=0) is True
    assert calls["n"] == 3 and not target.exists()


def test_remove_tree_warns_instead_of_masking_the_scenario_error(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(server.shutil, "rmtree", lambda path: (_ for _ in ()).throw(PermissionError("locked")))
    assert server._remove_tree(tmp_path, attempts=2, delay_s=0) is False
    assert "could not remove scratch directory" in capsys.readouterr().err


def test_remove_tree_of_a_missing_directory_is_fine(tmp_path):
    assert server._remove_tree(tmp_path / "gone") is True


def test_wait_for_ready_fails_fast_when_the_server_crashes(tmp_path):
    log = tmp_path / "server.log"
    with log.open("w", encoding="utf-8") as handle:
        process = subprocess.Popen([sys.executable, "-c", "print('boom: bad config'); raise SystemExit(4)"],
                                   stdout=handle, stderr=handle)
    started = time.monotonic()
    with pytest.raises(RuntimeError, match=r"(?s)exited \(code 4\).*boom"):
        server._wait_for_ready(process, log, port=9)
    assert time.monotonic() - started < server.STARTUP_TIMEOUT_S / 2


def test_kill_process_tree_stops_a_long_running_child_and_is_idempotent():
    process = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    server._kill_process_tree(process)
    assert process.poll() is not None
    server._kill_process_tree(process)  # already dead: must not raise
