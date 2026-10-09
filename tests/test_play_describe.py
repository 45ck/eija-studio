"""Describe your app (ADR-0203): one description makes a whole system, every view of it derived or recorded by the
kernel, and "What's missing" lists what each view still lacks."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from eija_studio.adapters.system_describer import OfflineSystemDescriber
from eija_studio.adapters.system_library import SystemLibrary
from eija_studio.application.describe_system import describe_documents
from eija_studio.domain.data import data_for
from eija_studio.domain.pack import PACKS_ROOT, PackError
from eija_studio.domain.scenarios import scenarios_for
from eija_studio.interfaces.http import create_app
from eija_studio.interfaces.play_systems import StudioHandle, Systems
from kernel_support import harness_studio

SESSION = "synthetic-describe-test"
HEADERS = {"Authorization": "Bearer " + SESSION, "Origin": "http://127.0.0.1:8765"}
COFFEE = ("A coffee shop app. Customers order drinks, baristas make them, then customers collect them. "
          "Orders have a size (small, medium, large), notes and a price.")


@pytest.fixture
def served(tmp_path):
    launched = PACKS_ROOT / "library-loan"
    studio = harness_studio(tmp_path / "workspace", pack=launched)
    handle = StudioHandle(studio)
    systems = Systems(handle, SystemLibrary(tmp_path / "home"), lambda pack, workspace: harness_studio(workspace, pack=pack),
                      launched, tmp_path / "workspace", describer=OfflineSystemDescriber())
    app = create_app(handle, SESSION, systems=systems)
    yield TestClient(app, base_url=HEADERS["Origin"]), systems
    app.state.play.stop()


def post(client, path, body):
    response = client.post(path, json=body, headers=HEADERS)
    assert response.status_code == 200, response.text
    return response.json()


def test_a_description_becomes_a_whole_system(served):
    client, systems = served
    checked = post(client, "/api/play/systems/new", {"template": "describe", "description": COFFEE, "check_only": True})
    assert not checked["created"] and not checked["problems"]
    system = checked["system"]
    assert system["record"] == "Order" and system["roles"] == ["Barista", "Customer"]
    assert system["fields"] == ["title", "size", "notes", "price"]
    assert system["tests"] == ["Order reaches Collected", "Order reaches Cancelled", "Customer cannot Start"]
    assert checked["described"]["provider"] == "offline-describe-fixture-v1" and not checked["described"]["live"]
    assert "not a live model" in checked["described"]["reading"][0]

    created = post(client, "/api/play/systems/new", {"template": "describe", "description": COFFEE, "name": "Coffee shop"})
    assert created["created"]
    pack = systems.handle.pack
    assert pack.pack.name == "Coffee shop" and not pack.laws  # a law is the person's to write
    assert [a.name for a in data_for(pack).entity("Order").attributes] == ["title", "size", "notes", "price"]
    tests = post(client, "/api/play/tests", {})
    assert tests["status"] == "PASS" and tests["passed"] == 3

    # Every view is there: the built app passes conformance, and sequences come from the recorded tests.
    built = post(client, "/api/play/build", {})
    assert built["conformance"]["status"] == "PASS"
    sequences = post(client, "/api/play/sequences", {})
    assert len(sequences["sequences"]) == 3

    ready = post(client, "/api/play/ready", {})
    rows = {v["view"]: v for v in ready["views"]}
    assert rows["states"]["ready"] and rows["classes"]["ready"] and rows["screens"]["ready"] and rows["tests"]["ready"]
    assert not rows["laws"]["ready"] and "No laws" in rows["laws"]["items"][0]["text"]

    # A chat round that adds a state nothing reaches and an untested action shows up in What's missing.
    plan = [{"kind": "add_state", "state": "Refunded"}]
    after = {v["view"]: v for v in post(client, "/api/play/ready", {"plan": plan})["views"]}
    assert any("Refunded cannot be reached" in i["text"] for i in after["states"]["items"])
    assert len(scenarios_for(pack).scenarios) == 3  # nothing was written


def test_the_describer_answer_is_checked_like_any_system(tmp_path):
    class Bad:
        name, live = "bad", False

        def describe(self, text):
            return {"record": "Order", "sketch": "Placed -> Done : Finish [Staff]", "fields": [{"name": "Bad Name", "type": "text"}]}

    with pytest.raises(PackError):
        describe_documents("anything", "X", lambda name: "x", Bad())
    with pytest.raises(PackError):
        describe_documents("", "X", lambda name: "x", OfflineSystemDescriber())


@pytest.mark.parametrize("text, record, template", [
    ("a helpdesk where customers raise tickets and engineers fix them", "Ticket", "tickets"),
    ("gym class booking for members and trainers", "Booking", "bookings"),
    ("expense approval: employees submit, managers approve, finance pays", "Request", "approvals"),
    ("track my plants, with a watering date", "Plant", "plain"),
])
def test_offline_shapes(text, record, template):
    documents, reading = describe_documents(text, "", lambda name: "sys", OfflineSystemDescriber())
    assert documents["data.json"]["record"] == record and reading["template"] == template
    assert documents["scenarios.json"]["scenarios"]
