"""The system landscape (ADR-0203): workflows that share a class form one system, drawn as one component diagram, and
the places where their class diagrams disagree are found. Each check has a negative case where the copies agree."""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from eija_studio.application.landscape import landscape
from eija_studio.domain.data import DataModel, data_for
from eija_studio.domain.pack import PACKS_ROOT, load_pack
from eija_studio.interfaces.http import create_app
from kernel_support import harness_studio

ROOT = Path(__file__).resolve().parents[1]
SESSION = "synthetic-landscape-test"
HEADERS = {"Authorization": "Bearer " + SESSION, "Origin": "http://127.0.0.1:8765"}


def shipped(*ids: str):
    packs = [load_pack(PACKS_ROOT / i) for i in ids]
    return [(p, data_for(p), p.model) for p in packs]


def with_data(pack_id: str, data: dict):
    """A shipped workflow with another class diagram, as a person's edit of `data.json` would give it."""
    pack = load_pack(PACKS_ROOT / pack_id)
    return pack, DataModel.model_validate({"id": pack_id, **data}), pack.model


def codes(result) -> list[str]:
    return [f["code"] for f in result["findings"]]


def test_the_library_workflows_form_one_system_and_the_excursion_is_elsewhere():
    result = landscape("library-loan", shipped("library-loan", "library-fines", "excursion"))
    assert [w["id"] for w in result["workflows"]] == ["library-fines", "library-loan"]
    assert result["elsewhere"] == ["excursion"]
    # Fines names Loan, which library-loan moves, so fines uses library-loan through it.
    assert result["links"] == [{"source": "library-fines", "target": "library-loan", "class": "Loan"}]
    assert {c["name"]: c["owner"] for c in result["classes"]} == {"Loan": "library-loan", "Member": None}
    # Roles of the same name are one actor, holding the actions its transitions name in each workflow.
    librarian = next(a for a in result["actors"] if a["name"] == "Librarian")
    assert librarian["workflows"]["library-loan"] == ["CheckOut", "Return", "ReturnLate"]
    assert librarian["workflows"]["library-fines"] == ["Uphold", "Concede", "Waive"]
    assert result["limits"] and "#93" in result["limits"][0]


def test_a_class_no_workflow_moves_and_its_differing_copies_are_found():
    result = landscape("library-fines", shipped("library-loan", "library-fines"))
    assert codes(result) == ["CLASS_HAS_NO_OWNER", "CLASS_COPIES_DIFFER"]
    differ = result["findings"][1]
    assert differ["subject"] == ["class:Member", "attribute:Member.card"]
    assert "text max 32 required in library-fines" in differ["message"] and "text max 20 required in library-loan" in differ["message"]
    assert result["counts"] == {"warning": 1, "consider": 1}


def test_a_workflow_alone_is_a_system_of_one_with_nothing_to_find():
    result = landscape("excursion", shipped("excursion", "library-loan"))
    assert [w["id"] for w in result["workflows"]] == ["excursion"]
    assert result["links"] == [] and result["findings"] == [] and result["elsewhere"] == ["library-loan"]


def test_copies_that_agree_are_not_findings():
    loan = data_for(load_pack(PACKS_ROOT / "library-loan"))
    member = loan.entity("Member").model_dump(mode="json")
    agreeing = {"record": "Fine", "entities": [{"name": "Fine", "attributes": [{"name": "amount", "type": "number"}]},
                                               {"name": "Loan", "attributes": [{"name": "dueDate", "type": "date", "required": True}]}, member]}
    result = landscape("library-fines", [*shipped("library-loan"), with_data("library-fines", agreeing)])
    assert codes(result) == ["CLASS_HAS_NO_OWNER"]  # Member is still nobody's record; its copies agree


def test_an_attribute_added_to_a_class_another_workflow_owns_is_found():
    adds = {"record": "Fine", "entities": [{"name": "Fine", "attributes": []},
                                           {"name": "Loan", "attributes": [{"name": "dueDate", "type": "date", "required": True},
                                                                           {"name": "fineTotal", "type": "number"}]}]}
    result = landscape("library-fines", [*shipped("library-loan"), with_data("library-fines", adds)])
    assert codes(result) == ["ATTRIBUTE_NOT_ON_OWNER"]
    assert result["findings"][0]["subject"] == ["class:Loan", "attribute:Loan.fineTotal"]


def test_two_workflows_moving_one_record_are_found_and_not_linked():
    twice = {"record": "Loan", "entities": [{"name": "Loan", "attributes": [{"name": "dueDate", "type": "date", "required": True}]}]}
    result = landscape("library-fines", [*shipped("library-loan"), with_data("library-fines", twice)])
    assert codes(result) == ["RECORD_MOVED_TWICE"] and result["links"] == []


def test_a_notification_to_no_role_in_the_system_is_found():
    pack = load_pack(PACKS_ROOT / "library-loan")
    renamed = pack.model_copy(update={"roles": tuple(r.model_copy(update={"id": "Borrower"}) if r.id == "Member" else r for r in pack.roles)})
    result = landscape("library-loan", [(renamed, data_for(pack), pack.model)])
    assert set(codes(result)) == {"RECIPIENT_IS_NOT_AN_ACTOR"}
    assert landscape("library-loan", shipped("library-loan"))["findings"] == []  # recipient "member" is the Member role


@pytest.fixture
def client(tmp_path):
    app = create_app(harness_studio(tmp_path / "workspace", pack=PACKS_ROOT / "library-loan"), SESSION)
    yield TestClient(app, base_url=HEADERS["Origin"])
    app.state.play.stop()


def test_the_route_reads_the_packs_beside_the_open_one(client):
    response = client.post("/api/play/landscape", json={}, headers=HEADERS)
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["format"] == "eija.landscape.v1" and result["focus"] == "library-loan"
    assert "library-fines" in [w["id"] for w in result["workflows"]] and "excursion" in result["elsewhere"]
    assert result["unreadable"] == []


def test_the_page_loads_the_system_lens_after_play_js(client):
    page = client.get("/play").text
    assert page.index("/assets/play.js") < page.index("/assets/play-landscape.js")
    for name in ("play-landscape.js", "play-landscape.css"):
        assert client.get(f"/assets/{name}").status_code == 200
    source = (ROOT / "src/eija_studio/resources/web/play-landscape.js").read_text(encoding="utf-8")
    assert "fetch(" not in source  # it asks the server through the page's api(); the server decides


def test_a_notification_no_transition_requires_is_not_published():
    pack = load_pack(PACKS_ROOT / "library-loan")
    unused = pack.effects.model_copy(update={"catalog": (*pack.effects.catalog, pack.effects.catalog[1].model_copy(update={"id": "Notification:Unused", "recipient": "nobody"}))})
    result = landscape("library-loan", [(pack.model_copy(update={"effects": unused}), data_for(pack), pack.model)])
    loan = result["workflows"][0]
    assert "Notification:Unused" not in [p["effect"] for p in loan["publishes"]] and result["findings"] == []


def test_a_second_folder_with_a_taken_id_is_reported_not_merged(tmp_path):
    import shutil  # noqa: PLC0415

    for name in ("library-loan", "library-fines"):
        shutil.copytree(PACKS_ROOT / name, tmp_path / name)
    shutil.copytree(PACKS_ROOT / "library-fines", tmp_path / "fines-copy")
    app = create_app(harness_studio(tmp_path / "workspace", pack=tmp_path / "library-loan"), SESSION)
    try:
        result = TestClient(app, base_url=HEADERS["Origin"]).post("/api/play/landscape", json={}, headers=HEADERS).json()
    finally:
        app.state.play.stop()
    assert [w["id"] for w in result["workflows"]] == ["library-fines", "library-loan"]
    assert result["unreadable"] == ["library-fines (its id library-fines is taken)"]


def test_each_actor_carries_the_kind_its_workflows_declare_and_a_disagreement_shows():
    loan, fines = load_pack(PACKS_ROOT / "library-loan"), load_pack(PACKS_ROOT / "library-fines")
    # Fines hands disputes to an AI agent that loan does not know, and calls its clerk a timer where loan has a person.
    roles = [*fines.roles, fines.roles[0].model_copy(update={"id": "Clerk", "kind": "timer"}),
             fines.roles[0].model_copy(update={"id": "DisputeBot", "kind": "agent"})]
    fines = fines.model_copy(update={"roles": roles})
    result = landscape("library-loan", [(p, data_for(p), p.model) for p in (loan, fines)])
    kinds = {a["name"]: a["kinds"] for a in result["actors"]}
    assert kinds["Librarian"] == ["human"]
    assert kinds["DisputeBot"] == ["agent"]  # declared only by the other workflow, and still not a person
    assert kinds["Clerk"] == ["human", "timer"]
