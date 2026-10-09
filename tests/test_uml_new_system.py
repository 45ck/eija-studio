"""Start a new system from a UML file (ADR-0190 with ADR-0185): the file's model becomes the new pack.

The kernel's pack check and protected policy judge it before anything is created, and the report names every element
read, kept or filled in, or not imported, as an import into an existing system does.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from eija_studio.adapters.system_library import SystemLibrary
from eija_studio.application.interop import FORMATS, export_model, start_from_file
from eija_studio.domain.data import data_for
from eija_studio.domain.pack import PACKS_ROOT, PackError, load_pack, parse_pack
from eija_studio.interfaces.cli import main
from eija_studio.interfaces.http import create_app
from eija_studio.interfaces.play_systems import StudioHandle, Systems
from kernel_support import harness_studio

SESSION = "synthetic-uml-new-system-test"
HEADERS = {"Authorization": "Bearer " + SESSION, "Origin": "http://127.0.0.1:8765"}
PACKS = sorted(p.name for p in PACKS_ROOT.iterdir() if (p / "pack.json").is_file())
DESK = """@startuml
[*] --> Open
Open --> Triaged : Triage [role = Agent] / Audit:Triaged
Triaged --> Resolved : Resolve [role = Agent and assigned] / Audit:Resolved, Notification:CustomerTold
Triaged --> Escalated : Escalate
Escalated --> Resolved : Fix [role = Engineer and severity > 2]
Escalated --> Resolved : Resolve [role = Engineer]
Escalated --> "Waiting on vendor" : Wait [role = Engineer]
@enduml
@startuml
class Ticket <<record>> {
  +subject : String [1] {maxLength = 120}
  +urgent : Boolean [0..1]
}
@enduml
"""


def _shape(pack):
    return sorted((t.action, t.from_state, t.to_state, t.role, tuple(sorted(t.guards)), t.required_effects) for t in pack.model.transitions)


@pytest.mark.parametrize("fmt", FORMATS)
@pytest.mark.parametrize("name", PACKS)
def test_a_new_system_from_an_export_is_the_same_model(name, fmt):
    pack = load_pack(PACKS_ROOT / name)
    data = data_for(pack)
    text, _ = export_model(fmt, pack, None, data)
    documents, report = start_from_file(fmt, text, "Copy", "copy")
    copy = parse_pack(documents["pack.json"])
    assert report["status"] == "CLEAN", report["unmapped"]
    assert _shape(copy) == _shape(pack) and copy.model.initial_state == pack.model.initial_state
    if data is not None:
        assert documents["data.json"] | {"id": data.id} == data.model_dump(mode="json")


def test_a_hand_written_file_starts_a_system_and_every_loss_is_named():
    documents, report = start_from_file("plantuml", DESK, "Support desk", "support-desk")
    pack = parse_pack(documents["pack.json"])
    assert pack.model.initial_state == "Open" and pack.model.states == ("Open", "Triaged", "Resolved", "Escalated")
    resolve = pack.action("Resolve")
    assert "actor_assigned" in resolve.guards and resolve.required_effects == ("Audit:Resolved", "Notification:CustomerTold")
    assert pack.effect("Notification:CustomerTold").recipient == "agent"
    assert {r.id for r in pack.roles} == {"Agent", "User", "Engineer"}
    assert documents["data.json"]["record"] == "Ticket"
    assert [a["name"] for a in documents["data.json"]["entities"][0]["attributes"]] == ["subject", "urgent"]
    lost = {u["element"]: u["reason"] for u in report["unmapped"]}
    assert pack.action("Fix") is not None  # read, without the guard term it cannot hold
    assert "action Resolve already labels Triaged -> Resolved" in lost["transition Resolve (Escalated -> Resolved)"]
    assert "Fix: guard 'severity > 2'" in lost
    assert "is not a name" in lost["transition Wait (Escalated -> Waiting on vendor)"]
    assert "no imported transition" in lost["state Waiting on vendor"]
    kept = {d["element"] for d in report["defaulted"]}
    assert {"Escalate: role", "Fix: effects", "Resolve: Notification:CustomerTold recipient"} <= kept
    assert report["status"] == "PARTIAL"


def test_a_file_without_a_state_machine_is_refused():
    with pytest.raises(PackError) as error:
        start_from_file("mermaid", "classDiagram\n  class Ticket\n", "Desk", "desk")
    assert "no UML state machine" in error.value.diagnostics[0]


@pytest.fixture
def served(tmp_path):
    launched = PACKS_ROOT / "library-loan"
    studio = harness_studio(tmp_path / "workspace", pack=launched)
    handle = StudioHandle(studio)
    systems = Systems(handle, SystemLibrary(tmp_path / "home"), lambda pack, workspace: harness_studio(workspace, pack=pack),
                      launched, tmp_path / "workspace")
    app = create_app(handle, SESSION, systems=systems)
    yield TestClient(app, base_url=HEADERS["Origin"]), tmp_path
    app.state.play.stop()


def test_the_new_system_form_checks_a_uml_file_then_creates_and_opens_it(served):
    client, tmp = served
    body = {"name": "Support desk", "template": "uml", "filename": "desk.puml", "uml": DESK}
    checked = client.post("/api/play/systems/new", json=body | {"check_only": True}, headers=HEADERS).json()
    assert not checked["created"] and checked["system"]["record"] == "Ticket" and checked["import"]["status"] == "PARTIAL"
    assert not (tmp / "home" / "support-desk").exists()  # checking writes nothing
    created = client.post("/api/play/systems/new", json=body, headers=HEADERS).json()
    assert created["created"] and created["opened"]["id"] == "support-desk" and created["import"]["unmapped"]
    status = client.get("/api/status", headers=HEADERS).json()
    assert status["pack"]["id"] == "support-desk"
    empty = client.post("/api/play/systems/new", json=body | {"uml": "notes"}, headers=HEADERS).json()
    assert not empty["created"] and empty["problems"]


def test_eija_new_from_a_uml_file(tmp_path, capsys):
    source = tmp_path / "loan.xmi"
    assert main(["uml", "export", "--format", "xmi", "--pack", str(PACKS_ROOT / "library-loan"), "--out", str(source)]) == 0
    capsys.readouterr()
    assert main(["new", "Loans", "--uml", str(source), "--systems", str(tmp_path / "home")]) == 0
    created = json.loads(capsys.readouterr().out)
    assert created["import"]["status"] == "CLEAN" and Path(created["pack"]).name == "loans"
    assert _shape(load_pack(created["pack"])) == _shape(load_pack(PACKS_ROOT / "library-loan"))
