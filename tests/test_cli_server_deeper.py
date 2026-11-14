"""Regression tests for the second, deeper inspection of the `eija` command and the local server (2026-11-14,
docs/engineering/CLI-SERVER-INSPECTION.md, "Second pass"). Each test is named after the defect it pins (S1 to S8)."""
from __future__ import annotations

import json
import os
import shutil
import socket
import stat
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from eija_studio.adapters import system_library
from eija_studio.adapters.repository_capture import _metadata
from eija_studio.adapters.system_library import SystemLibrary
from eija_studio.application.interop import export_model
from eija_studio.domain.data import data_for
from eija_studio.domain.models import DomainError
from eija_studio.domain.pack import PACKS_ROOT, load_pack
from eija_studio.interfaces import cli, play
from eija_studio.interfaces.cli import main
from eija_studio.interfaces.http import BODY_LIMIT, create_app
from eija_studio.interfaces.play import AppRunner, _serves
from eija_studio.interfaces.play_systems import StudioHandle, Systems
from kernel_support import harness_studio

HEADERS = {"Authorization": "Bearer tok", "Origin": "http://127.0.0.1:8765"}
POSIX = pytest.mark.skipif(os.name == "nt", reason="POSIX permissions and shell filters")


def _run(*command: str) -> None:
    subprocess.run(command, check=True)  # noqa: S603 - a fixed git command on a repository the test made


def _client(app) -> TestClient:
    return TestClient(app, base_url="http://127.0.0.1:8765", raise_server_exceptions=False)


@POSIX
@pytest.mark.skipif(shutil.which("git") is None, reason="needs git")
def test_s1_reading_a_repository_never_runs_a_filter_its_git_config_names(tmp_path):
    repo, marker = tmp_path / "repo", tmp_path / "ran"
    repo.mkdir()
    git = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.invalid"]
    _run(*git, "init", "-q")
    (repo / ".gitattributes").write_text("*.txt filter=evil\n", encoding="utf-8")
    (repo / "a.txt").write_text("one\n", encoding="utf-8")
    _run(*git, "add", ".")
    _run(*git, "commit", "-qm", "init")
    # A checkout's own .git/config (a downloaded repository, say) names a command; .gitattributes points a file at it.
    _run(*git, "config", "filter.evil.clean", f"sh -c 'touch {marker}; cat'")
    _run(*git, "config", "filter.evil.process", f"sh -c 'touch {marker}'")
    _run(*git, "config", "filter.evil.required", "true")
    (repo / "a.txt").write_text("two\n", encoding="utf-8")  # stat-dirty: git status must compare its content
    metadata = _metadata(repo)
    assert not marker.exists()  # before the fix, `git status` ran the clean filter here
    assert metadata["dirty"] is True and metadata["head"]


def _xmi_upload(pack_name: str) -> dict:
    pack = load_pack(PACKS_ROOT / pack_name)
    text, _ = export_model("xmi", pack, pack.model, data_for(pack))
    return {"filename": f"{pack.id}.xmi", "text": text}


def test_s2_playide_imports_its_own_xmi_export_of_a_larger_pack(tmp_path):
    upload = _xmi_upload("building-permit")
    assert len(json.dumps(upload).encode()) > BODY_LIMIT  # 39 KB: over the old 32 KiB cap on every route
    app = create_app(harness_studio(tmp_path / "w", pack=PACKS_ROOT / "building-permit"), "tok")
    try:
        response = _client(app).post("/api/play/import", json=upload, headers=HEADERS)
    finally:
        app.state.play.stop()
    assert response.status_code == 200, response.json()
    assert response.json()["status"] == "CLEAN"


def test_s2_each_route_keeps_a_cap_its_contract_needs(tmp_path):
    client = _client(create_app(harness_studio(tmp_path / "w"), "tok"))
    big = {"request": "x" * (BODY_LIMIT + 10)}
    case = client.post("/api/cases", json=big, headers=HEADERS)
    assert case.status_code == 413 and case.json() == {"code": "BODY_TOO_LARGE", "message": "32 KiB request limit"}
    huge = {"filename": "a.xmi", "text": "x" * 5_000_000}
    assert client.post("/api/play/import", json=huge, headers=HEADERS).status_code == 413


def test_s3_the_built_app_stops_when_the_server_shuts_down(tmp_path):
    app = create_app(harness_studio(tmp_path / "w"), "tok")
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    try:
        with TestClient(app, base_url="http://127.0.0.1:8765"):  # runs the app's startup and shutdown, as uvicorn does
            app.state.play.process = child  # as if Build & run had started it
            assert child.poll() is None
        assert child.wait(timeout=10) is not None  # before the fix it outlived a SIGTERM'd server
    finally:
        if child.poll() is None:  # pragma: no cover - only on failure
            child.kill()


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


@POSIX
def test_s4_open_hands_the_browser_an_owner_only_file_not_the_private_link(tmp_path, monkeypatch, capsys):
    opened, seen = [], {}

    def serve(app, sock):
        page = Path(opened[0].removeprefix("file://"))
        seen["mode"] = stat.S_IMODE(page.stat().st_mode)
        seen["text"] = page.read_text(encoding="utf-8")

    monkeypatch.setattr("webbrowser.open", opened.append)
    monkeypatch.setattr(cli, "_serve", serve)
    assert main(["serve", "--open", "--port", str(_free_port()), "--workspace", str(tmp_path / "w")]) == 0
    token = capsys.readouterr().out.split("#", 1)[1].split()[0]
    assert len(opened) == 1 and opened[0].startswith("file://") and token not in opened[0]
    assert seen["mode"] == 0o600 and f"/#{token}" in seen["text"]
    assert not (tmp_path / "w" / cli.LAUNCHER).exists()  # removed when the server stops


class _Impostor(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps({"subject": {"digest": "someone-else"}}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def test_s5_a_port_taken_before_the_app_binds_it_is_not_reported_as_the_app(tmp_path, monkeypatch):
    impostor = ThreadingHTTPServer(("127.0.0.1", 0), _Impostor)
    threading.Thread(target=impostor.serve_forever, daemon=True).start()
    port = impostor.server_address[1]
    (tmp_path / "run.py").write_text("import time\ntime.sleep(60)\n", encoding="utf-8")  # an app that never binds
    monkeypatch.setattr(play, "_free_port", lambda: port)  # the race: another program took the free port first
    runner = AppRunner(lambda: tmp_path)
    try:
        assert _serves(port, "someone-else") and not _serves(port, "this-build")
        with pytest.raises(DomainError) as refused:
            runner._start(tmp_path, "this-build")
        assert refused.value.code == "APP_START_FAILED"
        assert runner.running is None and runner.process is None  # the child was stopped, nothing is framed
    finally:
        runner.stop()
        impostor.shutdown()
        impostor.server_close()


def test_s6_a_request_sees_one_system_even_if_another_is_opened_while_it_runs(tmp_path):
    launched, other = PACKS_ROOT / "library-loan", PACKS_ROOT / "excursion"
    handle = StudioHandle(harness_studio(tmp_path / "w", pack=launched))
    systems = Systems(handle, SystemLibrary(tmp_path / "home"), lambda pack, ws: harness_studio(ws, pack=pack),
                      launched, tmp_path / "w")
    app = create_app(handle, "tok", systems=systems)

    @app.get("/api/test/switch-midway")
    def switch_midway():
        before = handle.pack.id
        systems.open(other, tmp_path / "w2")  # another tab opens a different system now
        return {"before": before, "after": handle.pack.id, "current": systems.current["id"]}

    try:
        seen = _client(app).get("/api/test/switch-midway", headers=HEADERS).json()
    finally:
        app.state.play.stop()
    assert seen == {"before": "library-loan", "after": "library-loan", "current": "excursion"}
    assert handle.pack.id == "excursion"  # the next request is on the system opened


def test_s7_a_system_folder_made_while_one_is_being_written_is_system_exists(tmp_path, monkeypatch):
    library, write = SystemLibrary(tmp_path / "home"), system_library._write_json

    def racing(path, document):  # another `eija new`, or another tab, makes the same system meanwhile
        (tmp_path / "home" / "desk").mkdir(exist_ok=True)
        (tmp_path / "home" / "desk" / "pack.json").write_text("{}", encoding="utf-8")
        write(path, document)

    monkeypatch.setattr(system_library, "_write_json", racing)
    with pytest.raises(DomainError) as refused:
        library.create("desk", {"pack.json": {"pack": {"id": "desk"}}})
    assert refused.value.code == "SYSTEM_EXISTS"  # before: a bare OSError, a 500 in PlayIDE
    assert [p.name for p in (tmp_path / "home").iterdir()] == ["desk"]  # no staging folder left behind


def test_s7_two_new_systems_of_one_name_at_once_get_two_ids(tmp_path):
    launched = PACKS_ROOT / "library-loan"
    handle = StudioHandle(harness_studio(tmp_path / "w", pack=launched))
    systems = Systems(handle, SystemLibrary(tmp_path / "home"), lambda pack, ws: harness_studio(ws, pack=pack),
                      launched, tmp_path / "w")
    app = create_app(handle, "tok", systems=systems)
    client, answers = _client(app), []
    body = {"name": "Desk", "sketch": "Open -> Closed : Close [Clerk]\n"}
    threads = [threading.Thread(target=lambda: answers.append(client.post("/api/play/systems/new", json=body, headers=HEADERS)))
               for _ in range(3)]
    try:
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
    finally:
        app.state.play.stop()
    assert [a.status_code for a in answers] == [200, 200, 200]
    assert sorted(p.name for p in (tmp_path / "home").iterdir() if p.is_dir()) == ["desk", "desk-2", "desk-3"]


@POSIX
def test_s8_a_backup_is_owner_only_and_never_written_over_a_file(tmp_path, capsys):
    workspace, out = tmp_path / "w", tmp_path / "backup.sqlite3"
    assert main(["init", "--workspace", str(workspace)]) == 0
    assert main(["backup", "--workspace", str(workspace), "--out", str(out)]) == 0
    assert stat.S_IMODE(out.stat().st_mode) == 0o600  # before: 0644, though the database itself is 0600
    capsys.readouterr()
    assert main(["backup", "--workspace", str(workspace), "--out", str(out)]) == 2
    assert json.loads(capsys.readouterr().out)["error"] == "OUTPUT_EXISTS"
