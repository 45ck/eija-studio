"""PlayIDE systems (ADR-0185): start a system from a sketch or a template, open it again, and save the work in progress."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from eija_studio.adapters.system_library import SystemLibrary
from eija_studio.application.new_system import parse_sketch, sketch_documents, system_id, template_documents
from eija_studio.domain.data import data_for
from eija_studio.domain.pack import PACKS_ROOT, PackError, load_pack
from eija_studio.interfaces.http import create_app
from eija_studio.interfaces.cli import main
from eija_studio.interfaces.play_systems import StudioHandle, Systems
from kernel_support import harness_studio

SESSION = "synthetic-systems-test"
HEADERS = {"Authorization": "Bearer " + SESSION, "Origin": "http://127.0.0.1:8765"}
SKETCH = """# a support desk
Open -> Triaged : Triage [Agent]
Triaged -> Resolved : Resolve [Agent]
Triaged -> Escalated : Escalate [Agent]
Escalated -> Resolved : Fix [Engineer]
actions: Reopen
"""


@pytest.fixture
def served(tmp_path):
    launched = PACKS_ROOT / "library-loan"
    studio = harness_studio(tmp_path / "workspace", pack=launched)
    handle = StudioHandle(studio)
    systems = Systems(handle, SystemLibrary(tmp_path / "home"), lambda pack, workspace: harness_studio(workspace, pack=pack),
                      launched, tmp_path / "workspace")
    app = create_app(handle, SESSION, systems=systems)
    yield TestClient(app, base_url=HEADERS["Origin"]), systems, tmp_path
    app.state.play.stop()


def post(client, path, body):
    return client.post(path, json=body, headers=HEADERS)


def test_a_sketch_is_the_state_machine_in_its_own_label_notation():
    documents = sketch_documents("Support desk", "Ticket", SKETCH, "support-desk")
    model = documents["pack.json"]["model"]
    assert model["initial_state"] == "Open" and model["states"] == ["Open", "Triaged", "Resolved", "Escalated"]
    assert [(t["from_state"], t["action"], t["to_state"], t["role"]) for t in model["transitions"]][-1] == ("Escalated", "Fix", "Resolved", "Engineer")
    assert [a["id"] for a in documents["pack.json"]["actions"]] == ["Triage", "Resolve", "Escalate", "Fix", "Reopen"]
    assert documents["data.json"]["record"] == "Ticket" and documents["pack.json"]["laws"] == []


@pytest.mark.parametrize("sketch, problem", [
    ("Open -> Done", "line 1: write it as"),
    ("A -> B : Go [R]\nB -> C : Go [R]", "line 2: action Go already labels line 1"),
    ("", "sketch: One transition per line"),
    ("A -> B : Go [R]\nactions: 9bad", "line 2: '9bad' is not a name"),
])
def test_a_bad_sketch_is_refused_line_by_line(sketch, problem):
    with pytest.raises(PackError) as refused:
        parse_sketch(sketch)
    assert any(d.startswith(problem) for d in refused.value.diagnostics), refused.value.diagnostics


def test_a_record_must_be_a_uml_class_name():
    with pytest.raises(PackError, match="record"):
        sketch_documents("X", "ticket", SKETCH, "x")


def test_roles_that_slug_alike_still_get_their_own_users():
    documents = sketch_documents("Desk", "Ticket", "Open -> Done : Close [Agent]\nDone -> Open : Reopen [agent]\nroles: A_B, A__B", "desk")
    actors = documents["pack.json"]["fixtures"]["actors"]
    assert len({a["id"] for a in actors}) == len(actors) == 5
    assert [a["role"] for a in actors if a["active"]] == ["Agent", "agent", "A_B", "A__B"]


def test_ids_are_slugs_that_never_collide():
    assert system_id("Support desk!", set()) == "support-desk"
    assert system_id("Support desk", {"support-desk", "support-desk-2"}) == "support-desk-3"
    assert system_id("42", set()) == "system-42"


def test_a_template_copy_keeps_the_model_and_drops_what_was_the_templates_own():
    folder = PACKS_ROOT / "excursion"
    documents = {n: json.loads((folder / n).read_text(encoding="utf-8")) for n in ("pack.json", "data.json", "scenarios.json") if (folder / n).is_file()}
    copied = template_documents(load_pack(folder), documents, "Field trips", "field-trips")
    pack = copied["pack.json"]
    assert pack["pack"]["id"] == pack["model"]["id"] == copied["data.json"]["id"] == copied["scenarios.json"]["id"] == "field-trips"
    assert pack["laws"] == documents["pack.json"]["laws"]  # a copy keeps every law; nothing is loosened on the way
    assert pack["model"]["transitions"] == documents["pack.json"]["model"]["transitions"]
    assert all(not t["binds"] for t in pack["language"]["terms"])
    assert all(v["mode"] != "hand_encoded" for v in pack["verifiers"])


def test_check_only_says_what_would_be_created_and_writes_nothing(served):
    client, _systems, tmp = served
    result = post(client, "/api/play/systems/new", {"name": "Support desk", "record": "Ticket", "sketch": SKETCH, "check_only": True}).json()
    assert result["problems"] == [] and result["system"]["states"] == ["Open", "Triaged", "Resolved", "Escalated"]
    assert not (tmp / "home").exists()
    refused = post(client, "/api/play/systems/new", {"name": "Bad", "sketch": "Open -> Done", "check_only": True}).json()
    assert refused["created"] is False and refused["problems"]


def test_a_new_system_is_created_opened_and_runs_through_the_kernel(served):
    client, systems, tmp = served
    result = post(client, "/api/play/systems/new", {"name": "Support desk", "record": "Ticket", "sketch": SKETCH}).json()
    assert result["created"] and result["opened"]["id"] == "support-desk"
    folder = tmp / "home" / "support-desk"
    assert (folder / "pack.json").is_file() and (folder / "data.json").is_file() and (folder / ".eija").is_dir()
    status = client.get("/api/status", headers=HEADERS).json()
    assert status["pack"]["id"] == "support-desk" and status["pack"]["roles"] == ["Agent", "Engineer"]
    assert client.get("/api/play/data", headers=HEADERS).json()["data"]["record"] == "Ticket"
    simulated = post(client, "/api/play/simulate", {"seed": 3, "steps": 60}).json()
    assert simulated  # the kernel decided the run on the new system
    built = post(client, "/api/play/build", {}).json()
    assert built["conformance"]["status"] == "PASS" and built["cases"] > 0
    assert data_for(systems.handle.pack).record == "Ticket"



def test_a_new_system_names_its_own_files_and_does_not_offer_its_demo_request_to_the_chat(served):
    client, _, _ = served
    assert client.get("/api/status", headers=HEADERS).json()["pack"]["demo_modelled"] is True  # Library loan models its own
    post(client, "/api/play/systems/new", {"name": "Support desk", "record": "Ticket", "sketch": SKETCH})
    # A sketched system has no proposal rules, so the chat would refuse its demo request: the page offers typed steps.
    assert client.get("/api/status", headers=HEADERS).json()["pack"]["demo_modelled"] is False
    laws, tests = post(client, "/api/play/laws", {}).json(), post(client, "/api/play/tests", {}).json()
    assert laws["file"]["path"].endswith("home/support-desk/pack.json") and not laws["file"]["path"].startswith("packs/")
    assert tests["file"]["path"].endswith("home/support-desk/scenarios.json") and not tests["file"]["path"].startswith("packs/")

def test_a_template_system_and_reopening_the_one_the_server_started_with(served):
    client, _systems, tmp = served
    first = post(client, "/api/play/systems/new", {"name": "Trips", "template": "excursion"}).json()
    assert first["opened"]["id"] == "trips" and (tmp / "home" / "trips" / "scenarios.json").is_file()
    tests = post(client, "/api/play/tests", {}).json()
    assert tests["status"] == "PASS"  # the template's test cases run on the copy
    listing = client.get("/api/play/systems", headers=HEADERS).json()
    assert listing["current"]["id"] == "trips"
    assert [e["id"] for e in listing["recent"]] == ["library-loan"]  # the one the server started with, one click away
    assert {t["id"] for t in listing["templates"]} >= {"excursion", "library-loan"}
    back = post(client, "/api/play/systems/open", {"pack": listing["recent"][0]["pack"]}).json()
    assert back["opened"]["id"] == "library-loan"
    assert client.get("/api/status", headers=HEADERS).json()["pack"]["id"] == "library-loan"
    again = client.get("/api/play/systems", headers=HEADERS).json()
    assert [e["id"] for e in again["recent"]] == ["trips"]


def test_only_known_systems_can_be_opened(served):
    client, _systems, tmp = served
    stray = tmp / "elsewhere"
    stray.mkdir()
    (stray / "pack.json").write_text((PACKS_ROOT / "excursion" / "pack.json").read_text(encoding="utf-8"), encoding="utf-8")
    refused = post(client, "/api/play/systems/open", {"pack": str(stray)})
    assert refused.status_code == 404 and client.get("/api/status", headers=HEADERS).json()["pack"]["id"] == "library-loan"


def test_the_draft_is_saved_per_system_and_never_applied(served):
    client, systems, tmp = served
    step = {"kind": "add_state", "state": "Archived"}
    assert client.get("/api/play/draft", headers=HEADERS).json()["draft"] is None
    saved = post(client, "/api/play/draft", {"steps": [{"transaction": step, "author": "you"}], "accepted": [True]})
    assert saved.status_code == 200
    draft = client.get("/api/play/draft", headers=HEADERS).json()["draft"]
    assert draft["steps"][0]["transaction"] == step and draft["system"] == "library-loan" and len(draft["model"]) == 64
    assert (tmp / "workspace" / "draft.json").is_file()
    with systems.handle.store.transaction() as u:
        assert "Archived" not in u.active()["model"]["states"]  # saving is not applying
    post(client, "/api/play/systems/new", {"name": "Support desk", "record": "Ticket", "sketch": SKETCH})
    assert client.get("/api/play/draft", headers=HEADERS).json()["draft"] is None  # another system, another draft
    post(client, "/api/play/systems/open", {"pack": str(PACKS_ROOT / "library-loan")})
    assert client.get("/api/play/draft", headers=HEADERS).json()["draft"]["steps"][0]["transaction"] == step
    post(client, "/api/play/draft/clear", {})
    assert client.get("/api/play/draft", headers=HEADERS).json()["draft"] is None


def test_a_malformed_draft_step_or_screen_is_refused(served):
    client, _systems, _tmp = served
    assert post(client, "/api/play/draft", {"steps": [{"transaction": {"kind": "rm_rf"}}]}).status_code == 409
    assert post(client, "/api/play/draft", {"screens": {"schema_version": "eija.screens.v1", "id": "other", "screens": []}}).status_code == 409
    assert post(client, "/api/play/draft", {"steps": [{"transaction": {"kind": "add_state", "state": f"S{i}"}} for i in range(13)]}).status_code == 422


def test_the_page_loads_the_systems_controls(served):
    client, _, _ = served
    page = client.get("/play").text
    assert 'id="system-menu"' in page and 'id="systems-dialog"' in page and "/assets/play-systems.js" in page
    assert client.get("/assets/play-systems.js").status_code == 200 and client.get("/assets/play-systems.css").status_code == 200


def test_the_cli_starts_a_system_or_lists_the_problems(tmp_path, capsys):
    sketch = tmp_path / "desk.txt"
    sketch.write_text(SKETCH, encoding="utf-8")
    argv = ["new", "Support desk", "--sketch", str(sketch), "--record", "Ticket", "--systems", str(tmp_path / "home")]
    assert main(argv) == 0
    created = json.loads(capsys.readouterr().out)
    assert Path(created["pack"]).name == "support-desk" and load_pack(created["pack"]).model.initial_state == "Open"
    sketch.write_text("Open -> Done", encoding="utf-8")
    assert main(argv) == 2
    assert json.loads(capsys.readouterr().out)["problems"]
    assert main(["new", "Trips", "--from", "excursion", "--systems", str(tmp_path / "home")]) == 0
    assert json.loads(capsys.readouterr().out)["system"]["id"] == "trips"
