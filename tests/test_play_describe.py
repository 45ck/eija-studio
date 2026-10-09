"""Describe your app (ADR-0216): one description makes a whole system, every view of it derived or recorded by the
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


def test_an_ai_agent_a_timer_and_an_external_system_become_roles_of_their_kind(served):
    """ADR-0210 kinds from the describe box (#156): the verb picks the transition, and one with no matching action is
    still a role of its kind, which What's missing reports as taking no action."""
    client, systems = served
    text = ("A support desk. Customers raise tickets, an AI agent triages them, engineers fix escalated ones. "
            "A webhook reports outages.")
    created = post(client, "/api/play/systems/new", {"template": "describe", "description": text, "name": "Desk"})
    assert created["created"] and created["system"]["kinds"] == {"AiAgent": "agent", "ExternalSystem": "system"}
    pack = systems.handle.pack
    assert next(t.role for t in pack.model.transitions if t.action == "Triage") == "AiAgent"
    assert pack.role_kind("AiAgent") == "agent" and pack.role_kind("Customer") == "human"
    assert any("AiAgent is an AI agent, taking Triage" in line for line in created["described"]["reading"])
    ready = post(client, "/api/play/ready", {})
    roles = next(v for v in ready["views"] if v["view"] == "usecases")
    assert [i["text"] for i in roles["items"]] == ["ExternalSystem takes no action"]


def test_a_sketch_declares_the_kind_of_a_role(served):
    client, _ = served
    sketch = "Open -> Triaged : Triage [Bot]\nTriaged -> Closed : Close [Lead]\nagents: Bot\ntimers: Sweeper"
    checked = post(client, "/api/play/systems/new", {"template": "blank", "name": "Kinds", "record": "Case", "sketch": sketch, "check_only": True})
    assert not checked["problems"] and checked["system"]["kinds"] == {"Bot": "agent", "Sweeper": "timer"}
    clash = post(client, "/api/play/systems/new", {"template": "blank", "name": "Kinds", "record": "Case",
                                                   "sketch": sketch + "\nsystems: Bot", "check_only": True})
    assert clash["problems"] == ["line 5: Bot is already listed as another kind of actor"]


def test_update_the_tests_records_the_stale_ones_again_on_the_model_shown(served):
    """What's missing's "Update the tests" (ADR-0216): a recorded test a round made stale is recorded again by the
    kernel, a new way to an end state is added, one whose end is gone is dropped; nothing is written to the pack."""
    client, systems = served
    post(client, "/api/play/systems/new", {"template": "describe", "description": COFFEE, "name": "Coffee shop"})
    plan = [{"kind": "add_state", "state": "Paid"},
            {"kind": "add_transition", "id": "TR-PAY", "action": "Pay", "from_state": "Placed", "to_state": "Paid", "role": "Customer"},
            {"kind": "retarget_transition", "transition": "TR-START", "end": "source", "state": "Paid"},
            {"kind": "remove_transition", "transition": "TR-CANCEL"}, {"kind": "remove_state", "state": "Cancelled"}]
    ready = post(client, "/api/play/ready", {"plan": plan})
    tests = next(v for v in ready["views"] if v["view"] == "tests")
    ids = [i["id"] for i in tests["items"]]
    assert ids == ["test-fails:order-reaches-collected", "test-fails:order-reaches-cancelled", "untested:Pay"]
    assert {i.get("action") for i in tests["items"]} == {"update-tests"}

    updated = post(client, "/api/play/tests/update", {"plan": plan})
    assert updated["changes"] == [{"change": "recorded again", "title": "Order reaches Collected"},
                                  {"change": "removed", "title": "Order reaches Cancelled"}]
    collected = next(s for s in updated["document"]["scenarios"] if s["id"] == "order-reaches-collected")
    assert [s["action"] for s in collected["steps"]] == ["Pay", "Start", "Finish", "Collect"]
    after = post(client, "/api/play/ready", {"plan": plan, "scenarios": updated["document"]})
    assert next(v for v in after["views"] if v["view"] == "tests")["ready"]
    assert len(scenarios_for(systems.handle.pack).scenarios) == 3  # the pack's own file is untouched

    saved = post(client, "/api/play/draft", {"steps": [], "accepted": [], "scenarios": updated["document"]})
    assert saved["saved"]
    assert client.get("/api/play/draft", headers=HEADERS).json()["draft"]["scenarios"] == updated["document"]


def test_a_system_with_no_tests_can_have_them_recorded(served):
    """A sketch's system has no tests yet: What's missing says Sequences shows a draft, and "Update the tests" records
    the way to each end with the same drafting the Sequences tab uses (`sequence_draft.journeys`)."""
    client, _ = served
    sketch = "Open -> Doing : Start [Worker]\nDoing -> Done : Finish [Worker]"
    post(client, "/api/play/systems/new", {"template": "blank", "name": "Jobs", "record": "Job", "sketch": sketch})
    tests = next(v for v in post(client, "/api/play/ready", {})["views"] if v["view"] == "tests")
    assert tests["items"][0]["id"] == "no-tests" and tests["items"][0]["action"] == "update-tests"
    assert "Sequences shows a draft" in tests["items"][0]["text"]
    updated = post(client, "/api/play/tests/update", {})
    assert updated["changes"] == [{"change": "added", "title": "Job reaches Done"}]
