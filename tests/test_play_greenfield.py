"""Building a new system in chat, round after round (ADR-0201): each ask is planned on top of the rounds before it,
and on a system you started a step may name the states, actions and roles it lacks, declared as a sketch declares them."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from eija_studio.adapters.plan_proposals import OfflinePlanProposer
from eija_studio.adapters.system_library import SystemLibrary
from eija_studio.application.new_system import declare, sketch_documents
from eija_studio.application.plan import preview_plan, propose_plan
from eija_studio.domain.models import DomainError
from eija_studio.domain.pack import PACKS_ROOT, find_pack, parse_pack
from eija_studio.domain.transactions import parse_transaction
from eija_studio.interfaces.http import create_app
from eija_studio.interfaces.play_systems import StudioHandle, Systems
from kernel_support import harness_studio

SESSION = "synthetic-greenfield-test"
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


def post(client, path, body):
    response = client.post(path, json=body, headers=HEADERS)
    assert response.status_code == 200, response.text
    return response.json()


def new_system(client):
    created = post(client, "/api/play/systems/new", {"name": "Coffee orders", "record": "Order", "sketch": SKETCH})
    assert created["created"], created
    return client.get("/api/play/draft", headers=HEADERS).json()


def ask(client, request, earlier):
    result = post(client, "/api/play/plan", {"request": request, "plan": earlier or None})
    return [s["transaction"] for s in result["steps"]], result


def test_rounds_stack_and_the_vocabulary_grows_on_your_own_system(served):
    client, _ = served
    new_system(client)
    one, first = ask(client, "add Cancel from Placed to Cancelled for Customer", [])
    assert [s["kind"] for s in one] == ["add_state", "add_transition"]  # the state it needs comes first
    assert first["steps"][1]["text"] == "Add Cancel: Placed → Cancelled, by Customer (new action Cancel)"
    assert first["preview"]["legal"] and first["preview"]["declared"] == {"actions": ["Cancel"], "roles": []}

    # Round two is planned on top of round one: it can name what round one added, and a new role.
    two, second = ask(client, "allow Manager to Cancel then rename state Ready to AwaitingPickup", one)
    assert second["steps"][0]["text"] == "Let Manager take Cancel (new role Manager)"
    assert second["preview"]["legal"]

    # Round three goes back on round one: removing a state still in use removes its transitions first.
    three, third = ask(client, "remove state Cancelled", one + two)
    assert [s["kind"] for s in three] == ["remove_transition", "remove_state"]
    assert third["preview"]["legal"]

    steps = one + two + three
    preview = post(client, "/api/play/plan/preview", {"steps": steps, "accepted": [True] * len(steps)})
    assert preview["legal"] and preview["candidate"]["states"] == ["Placed", "Brewing", "AwaitingPickup", "Collected"]
    assert preview["declared"] == {"actions": ["Cancel"], "roles": ["Manager"]}  # declared by the steps, kept as a draft

    # Rejecting round three's steps brings Cancelled back; every view runs the grown system through the kernel.
    kept = one + two
    built = post(client, "/api/play/build", {"plan": kept})
    assert built["conformance"]["status"] == "PASS" and built["url"]
    simulated = post(client, "/api/play/simulate", {"plan": kept, "seed": 3, "steps": 60})
    assert simulated["steps"]
    access = post(client, "/api/play/access", {"plan": kept})
    assert "Manager" in str(access)


def test_the_saved_draft_keeps_each_rounds_ask(served):
    client, _ = served
    new_system(client)
    one, _ = ask(client, "add Cancel from Placed to Cancelled for Customer", [])
    saved = [{"transaction": tx, "author": "ai", "round": 1, "request": "add Cancel from Placed to Cancelled for Customer"} for tx in one]
    post(client, "/api/play/draft", {"steps": saved, "accepted": [True, True]})
    draft = client.get("/api/play/draft", headers=HEADERS).json()["draft"]
    assert [s["round"] for s in draft["steps"]] == [1, 1] and draft["steps"][0]["request"].startswith("add Cancel")


def test_a_shipped_packs_vocabulary_stays_fixed(served):
    client, _ = served  # the library-loan pack the server started with is not one you started
    response = client.post("/api/play/plan", json={"request": "add Teleport from OnLoan to Returned for Librarian"}, headers=HEADERS)
    assert response.status_code == 409 and response.json()["code"] == "PLAN_UNKNOWN_NAME"


def test_a_new_name_must_be_one_the_built_app_can_use():
    pack = parse_pack(sketch_documents("Coffee", "Order", SKETCH, "coffee")["pack.json"])
    with pytest.raises(DomainError) as refused:
        OfflinePlanProposer().propose("add Do-it from Placed to Ready for Barista", pack.model, pack, grows=True)
    assert refused.value.code == "PLAN_UNKNOWN_NAME"
    tx = parse_transaction({"kind": "add_transition", "id": "TR-X", "action": "start", "from_state": "Ready",
                            "to_state": "Placed", "role": "Barista"})
    with pytest.raises(DomainError) as clash:  # Start and start would hide each other in chat
        declare(pack, [tx])
    assert clash.value.code == "PLAN_NAME_INVALID"


def test_a_grown_pack_is_a_draft_no_case_can_name():
    pack = parse_pack(sketch_documents("Coffee", "Order", SKETCH, "coffee")["pack.json"])
    tx = parse_transaction({"kind": "add_transition", "id": "TR-CANCEL", "action": "Cancel", "from_state": "Placed",
                            "to_state": "Collected", "role": "Customer"})
    grown = declare(pack, [tx])
    assert grown.action("Cancel").required_effects == ("Audit:Cancel",) and grown.digest != pack.digest
    assert find_pack("coffee", digest=grown.digest) is None
    assert declare(pack, []) is pack


def test_without_grows_a_new_action_is_refused_as_before():
    pack = parse_pack(sketch_documents("Coffee", "Order", SKETCH, "coffee")["pack.json"])
    with pytest.raises(DomainError, match="declares no action Cancel"):
        propose_plan("add Cancel from Placed to Collected for Customer", pack.model, pack, OfflinePlanProposer())
    tx = parse_transaction({"kind": "add_transition", "id": "TR-CANCEL", "action": "Cancel", "from_state": "Placed",
                            "to_state": "Collected", "role": "Customer"})
    assert not preview_plan(pack.model, pack, [tx], [True])["legal"]
    assert preview_plan(pack.model, pack, [tx], [True], grows=True)["legal"]


def test_no_follow_on_is_proposed_when_every_action_is_in_use():
    pack = parse_pack(sketch_documents("Coffee", "Order", SKETCH, "coffee")["pack.json"])
    ripple = {"problems": [{"code": "STATE_UNREACHABLE", "ref": "state:Paid"}]}
    model = pack.model.model_copy(update={"states": (*pack.model.states, "Paid")})
    assert OfflinePlanProposer().follow_on(ripple, model, pack) == {"steps": []}
