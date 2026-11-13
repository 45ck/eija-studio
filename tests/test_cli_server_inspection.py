"""Regression tests for the defects the 2026-11-13 Fagan inspection of the `eija` command and the local server found
(docs/engineering/CLI-SERVER-INSPECTION.md). Each test is named after the defect it pins (D1 to D9)."""
from __future__ import annotations

import json
import socket

from fastapi.testclient import TestClient

from eija_studio.adapters.system_library import SystemLibrary
from eija_studio.domain.pack import PACKS_ROOT, load_pack
from eija_studio.interfaces.cli import failure_report, main
from eija_studio.interfaces.http import create_app
from eija_studio.interfaces.play import app_environment
from eija_studio.interfaces.play_systems import StudioHandle, Systems
from kernel_support import harness_studio

SKETCH = "Open -> Closed : Close [Clerk]\n"


def _json(capsys) -> dict:
    return json.loads(capsys.readouterr().out)


def test_d1_a_busy_port_is_refused_before_any_link_is_printed_or_workspace_made(tmp_path, capsys):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as other:  # another program holds the port
        other.bind(("127.0.0.1", 0))
        other.listen(1)
        port = other.getsockname()[1]
        if port < 1024:  # pragma: no cover - ephemeral ports are unprivileged on every supported platform
            return
        assert main(["serve", "--port", str(port), "--workspace", str(tmp_path / "w")]) == 2
    out = capsys.readouterr().out
    assert json.loads(out)["error"] == "PORT_IN_USE"
    assert "http://" not in out  # no private link to the other program's page
    assert not (tmp_path / "w").exists()


def test_d2_the_built_app_does_not_inherit_provider_keys(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-synthetic")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "synthetic")
    monkeypatch.setenv("EIJA_SYSTEMS", "/somewhere")
    monkeypatch.setenv("PATH", "/usr/bin")
    env = app_environment(43210)
    assert env["PORT"] == "43210" and env["PATH"] == "/usr/bin"
    assert not {"OPENAI_API_KEY", "ANTHROPIC_API_KEY", "EIJA_SYSTEMS"} & set(env)


def test_d3_a_non_ascii_authorization_header_is_401_not_a_server_error(tmp_path):
    client = TestClient(create_app(harness_studio(tmp_path / "w"), "tok"), base_url="http://127.0.0.1:8765",
                        raise_server_exceptions=False)
    response = client.get("/api/status", headers={"Authorization": "Bearer ték".encode("latin-1")})
    assert response.status_code == 401 and response.json()["code"] == "SESSION_REQUIRED"
    assert client.get("/api/status", headers={"Authorization": "Bearer tok"}).status_code == 200


def test_d4_an_invalid_port_is_refused_before_the_workspace_is_made(tmp_path, capsys):
    assert main(["serve", "--port", "80", "--workspace", str(tmp_path / "w")]) == 2
    assert _json(capsys)["error"] == "CONFIGURATION"
    assert not (tmp_path / "w").exists()


def test_d5_an_unknown_provider_from_the_environment_is_named(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("EIJA_PROVIDER", "bogus")
    assert main(["list", "--workspace", str(tmp_path / "w")]) == 2
    failure = _json(capsys)
    assert failure["error"] == "CONFIGURATION" and "EIJA_PROVIDER" in failure["message"] and "offline" in failure["message"]
    assert not (tmp_path / "w").exists()


def test_d6_uml_export_of_a_model_the_policy_refuses_exits_2_and_still_writes(tmp_path, capsys):
    pack = load_pack(PACKS_ROOT / "excursion")
    model = pack.model.model_dump(mode="json")
    approve = next(t for t in model["transitions"] if t["action"] == "Approve")
    approve["role"] = "Teacher"  # the submitter approves their own excursion: PROTECTED_AUTHORITY
    workflow = tmp_path / "blocked.json"
    workflow.write_text(json.dumps(model), encoding="utf-8")
    out = tmp_path / "blocked.xmi"
    assert main(["uml", "export", "--format", "xmi", "--pack", str(PACKS_ROOT / "excursion"),
                 "--workflow", str(workflow), "--out", str(out)]) == 2
    assert "POLICY_BLOCKED: PROTECTED_AUTHORITY:Approve" in capsys.readouterr().err
    assert out.is_file()
    assert main(["uml", "export", "--format", "xmi", "--pack", str(PACKS_ROOT / "excursion"), "--out", str(out)]) == 0


def test_d7_file_and_folder_mixups_get_their_own_codes():
    assert failure_report(FileExistsError(17, "File exists", "x"))["error"] == "PATH_EXISTS"
    assert failure_report(NotADirectoryError(20, "Not a directory", "x"))["error"] == "NOT_A_DIRECTORY"


def test_d7_a_systems_home_that_is_a_file_is_named(tmp_path, capsys):
    home = tmp_path / "home"
    home.write_text("not a folder", encoding="utf-8")
    sketch = tmp_path / "sketch.txt"
    sketch.write_text(SKETCH, encoding="utf-8")
    assert main(["new", "Desk", "--sketch", str(sketch), "--systems", str(home)]) == 2
    assert _json(capsys)["error"] == "SYSTEMS_HOME_INVALID"


def test_d7_the_server_names_a_systems_home_that_is_a_file(tmp_path):
    home = tmp_path / "home"
    home.write_text("not a folder", encoding="utf-8")
    launched = PACKS_ROOT / "library-loan"
    handle = StudioHandle(harness_studio(tmp_path / "w", pack=launched))
    systems = Systems(handle, SystemLibrary(home), lambda pack, ws: harness_studio(ws, pack=pack), launched, tmp_path / "w")
    app = create_app(handle, "tok", systems=systems)
    client = TestClient(app, base_url="http://127.0.0.1:8765", raise_server_exceptions=False)
    try:
        response = client.post("/api/play/systems/new", json={"name": "Desk", "sketch": SKETCH},
                               headers={"Authorization": "Bearer tok", "Origin": "http://127.0.0.1:8765"})
    finally:
        app.state.play.stop()
    assert response.status_code == 409 and response.json()["code"] == "SYSTEMS_HOME_INVALID"


def test_d8_eija_new_names_the_argument_that_is_too_long_not_a_file(tmp_path, capsys):
    assert main(["new", "a" * 100, "--systems", str(tmp_path / "home")]) == 2
    result = _json(capsys)
    assert result["created"] is False and result["problems"][0].startswith("name: ")
    assert not (tmp_path / "home").exists()


def test_d9_eija_new_from_describe_says_where_describing_lives(tmp_path, capsys):
    assert main(["new", "Desk", "--from", "describe", "--systems", str(tmp_path / "home")]) == 2
    result = _json(capsys)
    assert result["created"] is False and "only in PlayIDE" in result["problems"][0]

