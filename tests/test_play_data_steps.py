"""Growing a system's class diagram in chat (ADR-0202): on a system you started, a plan step may add an attribute to a
class, remove one, or make one required or optional. The draft data model is held in memory; the built app's form,
its conformance tests and the UML export follow it, and nothing is written."""
from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from eija_studio.adapters.system_library import SystemLibrary
from eija_studio.application.data_steps import apply_data, data_changes, draft_pack, parse_step
from eija_studio.domain.data import data_for
from eija_studio.domain.models import DomainError
from eija_studio.domain.pack import PACKS_ROOT, load_pack
from eija_studio.interfaces.http import create_app
from eija_studio.interfaces.play_systems import StudioHandle, Systems
from kernel_support import harness_studio

SESSION = "synthetic-data-steps-test"
HEADERS = {"Authorization": "Bearer " + SESSION, "Origin": "http://127.0.0.1:8765"}
SKETCH = "Placed -> Brewing : Start [Barista]\nBrewing -> Ready : Finish [Barista]\nReady -> Collected : Collect [Customer]"


@pytest.fixture
def served(tmp_path):
    launched = PACKS_ROOT / "library-loan"
    studio = harness_studio(tmp_path / "workspace", pack=launched)
    handle = StudioHandle(studio)
    systems = Systems(handle, SystemLibrary(tmp_path / "home"), lambda pack, workspace: harness_studio(workspace, pack=pack),
                      launched, tmp_path / "workspace")
    app = create_app(handle, SESSION, systems=systems)
    yield TestClient(app, base_url=HEADERS["Origin"]), systems
    app.state.play.stop()


def post(client, path, body, status=200):
    response = client.post(path, json=body, headers=HEADERS)
    assert response.status_code == status, response.text
    return response.json()


def ask(client, request, earlier):
    result = post(client, "/api/play/plan", {"request": request, "plan": earlier or None})
    return [s["transaction"] for s in result["steps"]], result


def new_system(client, systems):
    created = post(client, "/api/play/systems/new", {"name": "Coffee orders", "record": "Order", "sketch": SKETCH})
    assert created["created"], created
    return systems.handle.pack


def test_chat_grows_the_record_class_and_the_built_app_follows(served):
    client, systems = served
    pack = new_system(client, systems)
    assert [a.name for a in data_for(pack).entity("Order").attributes] == ["title"]

    one, first = ask(client, "add field size as choice Small, Medium, Large required then add field notes", [])
    assert [s["text"] for s in first["steps"]] == ["Add attribute size: one of Small, Medium, Large to Order, required",
                                                   "Add attribute notes: text to Order"]
    assert first["preview"]["legal"] and first["preview"]["data_changes"] == ["Order gains size", "Order gains notes"]
    assert [a["name"] for a in first["preview"]["data"]["entities"][0]["attributes"]] == ["title", "size", "notes"]

    # A later round changes what an earlier one added, and mixes in a state-machine step.
    two, second = ask(client, "make notes required then add Cancel from Placed to Cancelled for Customer", one)
    assert second["steps"][0]["text"] == "Make Order.notes required" and second["preview"]["legal"]
    three, third = ask(client, "remove field notes", one + two)
    assert third["steps"][0]["text"] == "Remove attribute notes from Order" and third["preview"]["legal"]

    steps = one + two + three
    preview = post(client, "/api/play/plan/preview", {"steps": steps, "accepted": [True] * len(steps)})
    assert preview["legal"] and preview["data_changes"] == ["Order gains size"]
    assert "Cancelled" in preview["candidate"]["states"]

    # The form, the conformance tests and the class diagram's export all read the draft data model.
    built = post(client, "/api/play/build", {"plan": steps})
    assert built["conformance"]["status"] == "PASS" and built["url"]
    screens = post(client, "/api/play/screens", {"plan": steps})
    assert "size" in json.dumps(screens["screens"])
    exported = post(client, "/api/play/export", {"format": "plantuml", "plan": steps})
    assert "size" in exported["text"]
    rippled = post(client, "/api/play/ripple", {"plan": steps})
    assert any(i["text"] == "Order gains size" for i in rippled["diagrams"]["classes"])

    # The round alone reads against the rounds before it.
    since = one + two
    alone = post(client, "/api/play/ripple", {"plan": steps, "since": since})
    assert [i["text"] for i in alone["diagrams"]["classes"] if "notes" in i["text"]] == ["Order loses notes"]

    # Nothing was written: the system's data.json is the sketch's.
    assert [a.name for a in data_for(systems.handle.pack).entity("Order").attributes] == ["title"]

    # A saved draft keeps the data-model steps.
    saved = post(client, "/api/play/draft", {"steps": [{"transaction": s, "author": "ai"} for s in steps]})
    assert saved["saved"]


def test_a_shipped_pack_keeps_its_class_diagram(served):
    client, _ = served
    response = client.post("/api/play/plan", json={"request": "add field colour"}, headers=HEADERS)
    assert response.status_code == 409 and "PLAN_DATA_FIXED" in response.text
    step = {"kind": "add_attribute", "entity": "Loan", "attribute": {"name": "colour", "type": "text"}}
    preview = post(client, "/api/play/plan/preview", {"steps": [step], "accepted": [True]})
    assert not preview["legal"] and preview["steps"][0]["code"] == "PLAN_DATA_FIXED"
    refused = client.post("/api/play/build", json={"plan": [step]}, headers=HEADERS)
    assert refused.status_code == 409 and "PLAN_DATA_FIXED" in refused.text


def test_data_steps_that_cannot_apply_are_refused():
    pack = load_pack(PACKS_ROOT / "library-loan")
    data = data_for(pack)
    record = data.record
    bad = [
        {"kind": "add_attribute", "entity": "Nope", "attribute": {"name": "x", "type": "text"}},  # no such class
        {"kind": "add_attribute", "entity": record, "attribute": {"name": data.entity(record).attributes[0].name, "type": "text"}},
        {"kind": "remove_attribute", "entity": record, "name": "missing"},
        {"kind": "set_required", "entity": record, "name": "missing", "required": True},
    ]
    for step in bad:
        with pytest.raises(DomainError) as refused:
            apply_data(data, [parse_step(step)])
        assert refused.value.code == "EDIT_INVALID"
    for malformed in ({"kind": "add_attribute", "entity": record, "attribute": {"name": "Bad Name", "type": "text"}},
                      {"kind": "add_attribute", "entity": record, "attribute": {"name": "x", "type": "choice"}}):
        with pytest.raises(DomainError) as refused:
            parse_step(malformed)
        assert refused.value.code == "EDIT_INVALID"
    with pytest.raises(DomainError) as refused:
        draft_pack(pack, [parse_step({"kind": "remove_attribute", "entity": record, "name": "x"})], grows=False)
    assert refused.value.code == "PLAN_DATA_FIXED"


def test_a_held_data_model_leaves_the_pack_and_its_digest_alone():
    pack = load_pack(PACKS_ROOT / "library-loan")
    data = data_for(pack)
    step = parse_step({"kind": "add_attribute", "entity": data.record, "attribute": {"name": "colour", "type": "text"}})
    draft = draft_pack(pack, [step], grows=True)
    assert draft.digest == pack.digest and draft is not pack
    assert data_changes(data, data_for(draft)) == [f"{data.record} gains colour"]
    assert data_for(pack).digest == data.digest  # the loaded pack still reads its own data.json


def test_chat_says_who_holds_a_role(served):
    """#156 (ADR-0210, ADR-0216): "make Barista an AI agent" in chat is the same role-kind plan step the use case
    diagram makes; the simulated draft pack has the kind, and a role the system does not have is refused."""
    client, systems = served
    new_system(client, systems)
    steps, asked = ask(client, "make Barista an AI agent then Customer is a person", [])
    assert steps == [{"kind": "set_role_kind", "role": "Barista", "to": "agent"},
                     {"kind": "set_role_kind", "role": "Customer", "to": "human"}]
    assert asked["preview"]["legal"]
    pack = draft_pack(systems.handle.pack, [parse_step(s) for s in steps], True)
    assert pack.role_kind("Barista") == "agent" and systems.handle.pack.role_kind("Barista") == "human"
    _, unknown = ask(client, "make Nobody a timer", [])
    assert not unknown["preview"]["legal"]  # the system has no role Nobody


def test_a_round_that_only_sets_a_kind_builds_and_runs_another_app(served):
    """A role's kind is part of the built app (ADR-0215), so the running app is not reused when only a kind changed."""
    client, systems = served
    new_system(client, systems)
    play = client.app.state.play
    first = post(client, "/api/play/build", {})
    key = play.running["key"]
    steps, _ = ask(client, "make Barista an AI agent", [])
    second = post(client, "/api/play/build", {"plan": steps})
    assert first["url"] and second["url"] and play.running["key"] != key
