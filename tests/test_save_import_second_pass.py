"""Regression tests for the second inspection of saving and UML import (2026-11-14, ADR-0253).

The first pass (ADR-0245) read the code for partial reads and a tab on another system. This one round-trips every
shipped pack through all four formats with the kernel features they use, edits the files as a person would (rename a
state), gives names and text that a format writes differently, and puts two tabs on one system.
"""
from __future__ import annotations

import json
import re

import pytest

from eija_studio.application.interop import FORMATS, export_model, import_model
from eija_studio.domain.data import DataModel, load_data
from eija_studio.domain.models import Workflow
from eija_studio.domain.pack import PACKS_ROOT, load_pack
from test_play_systems import HEADERS, post, served  # noqa: F401  (the served fixture)

DESK, LOAN = PACKS_ROOT / "refund-desk", PACKS_ROOT / "library-loan"


def _loaded(folder):
    pack = load_pack(folder)
    return pack, load_data(folder, pack.id)


def _named(model: Workflow, old: str, new: str) -> Workflow:
    return Workflow.model_validate(json.loads(json.dumps(model.model_dump(mode="json")).replace(json.dumps(old), json.dumps(new))))


# ---- D11: a state renamed in a file was planned as remove + add ---------------------------------------------------

@pytest.mark.parametrize("fmt", FORMATS)
@pytest.mark.parametrize("state", ["WithSupervisor", "AwaitingApproval", "PayoutFailed"])
def test_a_state_renamed_in_a_file_is_renamed_and_keeps_its_composite(fmt, state):
    pack, data = _loaded(DESK)
    text = re.sub(rf"\b{state}\b", state + "Now", export_model(fmt, pack, data=data)[0])
    report = import_model(fmt, text, pack, data=data)
    machine = report["state_machine"]
    assert report["status"] == "CLEAN", report["unmapped"]
    assert machine["transactions"] == [{"kind": "rename_state", "state": state, "to": state + "Now"}]
    expected = json.loads(json.dumps(pack.model.model_dump(mode="json")["composites"]).replace(f'"{state}"', f'"{state}Now"'))
    assert machine["candidate"]["composites"] == expected


def test_two_renamed_states_are_each_matched_by_their_own_arrows():
    pack, data = _loaded(LOAN)
    text = export_model("plantuml", pack, data=data)[0]
    report = import_model("plantuml", re.sub(r"\bReturned\b", "Closed", re.sub(r"\bCancelled\b", "Dropped", text)), pack, data=data)
    assert sorted((t["state"], t["to"]) for t in report["state_machine"]["transactions"]) == [("Cancelled", "Dropped"), ("Returned", "Closed")]


def test_a_state_added_beside_a_renamed_one_is_added():
    pack, data = _loaded(LOAN)
    text = export_model("plantuml", pack, data=data)[0]
    # A state added beside a renamed one carries no arrows, so it is added, not taken for the renamed state.
    text = re.sub(r"\bCancelled\b", "Dropped", text).replace("state Dropped", "state Dropped\nstate Spare")
    steps = import_model("plantuml", text, pack, data=data)["state_machine"]["transactions"]
    assert {"kind": "add_state", "state": "Spare"} in steps and {"kind": "rename_state", "state": "Cancelled", "to": "Dropped"} in steps


# ---- D12: PlantUML wrote a double quote as a single quote, and read a state named like a keyword as another line ---

@pytest.mark.parametrize("name", ['Can"celled', "state", "end", "note", "title", "hide", "'quoted'", "a/'b", "Don't"])
def test_plantuml_gives_back_the_state_name_it_wrote(name):
    pack, data = _loaded(LOAN)
    model = _named(pack.model, "Returned", name)
    report = import_model("plantuml", export_model("plantuml", pack, model=model, data=data)[0], pack, model=model, data=data)
    # The status may be REFUSED: the pack's laws still name Returned (ADR-0250). The file itself must change nothing.
    machine = report["state_machine"]
    assert machine["transactions"] == [] and not machine["changed"] and report["unmapped"] == [], machine["transactions"]


@pytest.mark.parametrize("choice", ['a"b', "'q'"])
def test_plantuml_gives_back_an_enumeration_literal_it_wrote(choice):
    pack, data = _loaded(DESK)
    raw = data.model_dump(mode="json")
    next(a for a in raw["entities"][0]["attributes"] if a["type"] == "choice")["choices"][1] = choice
    changed = DataModel.model_validate(raw)
    report = import_model("plantuml", export_model("plantuml", pack, data=changed)[0], pack, data=changed)
    assert report["status"] == "CLEAN" and not report["class_model"]["changed"]


# ---- D13: spacing no UML file keeps came back as a change ---------------------------------------------------------

@pytest.mark.parametrize("fmt", FORMATS)
@pytest.mark.parametrize("name", ["On\tloan", "Returned ", "Re  turned"])
def test_a_state_name_differing_only_in_spacing_is_the_same_state(fmt, name):
    pack, data = _loaded(LOAN)
    model = _named(pack.model, "Returned", name)
    report = import_model(fmt, export_model(fmt, pack, model=model, data=data)[0], pack, model=model, data=data)
    assert report["state_machine"]["transactions"] == [] and not report["state_machine"]["changed"]


@pytest.mark.parametrize("fmt", FORMATS)
def test_descriptions_and_literals_differing_only_in_spacing_are_kept(fmt):
    pack, data = _loaded(DESK)
    raw = data.model_dump(mode="json")
    raw["entities"][0]["description"] = "One refund\nrequest,  two lines"
    raw["entities"][0]["attributes"][0]["description"] = "  padded\tnote "
    next(a for a in raw["entities"][0]["attributes"] if a["type"] == "choice")["choices"][1] = " Late  delivery"
    spaced = DataModel.model_validate(raw)
    report = import_model(fmt, export_model(fmt, pack, data=spaced)[0], pack, data=spaced)
    assert report["status"] == "CLEAN" and not report["class_model"]["changed"], report["class_model"].get("changes")


# ---- D14: Mermaid said it does not carry attribute descriptions, and its import then deleted them -----------------

def test_mermaid_keeps_the_attribute_descriptions_it_cannot_carry():
    pack, data = _loaded(DESK)
    raw = data.model_dump(mode="json")
    raw["entities"][0]["attributes"][0]["description"] = "The shop's order number"
    noted = DataModel.model_validate(raw)
    text, exported = export_model("mermaid", pack, data=noted)
    assert any("attribute descriptions" in x for x in exported["not_carried"])
    report = import_model("mermaid", text, pack, data=noted)
    assert not report["class_model"]["changed"]
    assert any(d["element"].endswith("orderNumber: description") for d in report["defaulted"])


# ---- D15: two tabs on one system saved over each other's work unseen ----------------------------------------------

def test_a_save_over_work_another_tab_saved_is_refused_until_pressed_again(served):  # noqa: F811
    client, systems, _tmp = served
    pack = systems.current["pack"]
    step = lambda state: {"steps": [{"transaction": {"kind": "add_state", "state": state}}], "pack": pack}  # noqa: E731
    first = post(client, "/api/play/draft", step("Archived") | {"base": None}).json()
    assert first["revision"]
    second = post(client, "/api/play/draft", step("Shelved") | {"base": first["revision"]}).json()  # the other tab, which saw it
    stale = post(client, "/api/play/draft", step("Archived") | {"base": first["revision"]})  # the first tab again
    assert stale.status_code == 409 and stale.json()["code"] == "DRAFT_CHANGED"
    assert post(client, "/api/play/draft/clear", {"pack": pack, "base": first["revision"]}).status_code == 409
    kept = client.get("/api/play/draft", headers=HEADERS).json()["draft"]
    assert kept["steps"][0]["transaction"]["state"] == "Shelved" and kept["revision"] == second["revision"]
    # Pressed again, knowing: the page sends the revision it was refused on, and the save replaces it.
    assert post(client, "/api/play/draft", step("Archived") | {"base": second["revision"]}).status_code == 200
    # A first save on a system with saved work is checked too; a caller that sends no base is not.
    assert post(client, "/api/play/draft", step("Other") | {"base": None}).status_code == 409
    assert post(client, "/api/play/draft", step("Other")).status_code == 200


# ---- D17: listing the templates moved the open system's files to the shipped pack's folder -------------------------

def test_listing_templates_does_not_move_the_open_systems_files(tmp_path):
    import shutil  # noqa: PLC0415

    from eija_studio.domain.data import data_for  # noqa: PLC0415
    from eija_studio.interfaces.play_systems import templates  # noqa: PLC0415

    copy = tmp_path / "refund-desk"
    shutil.copytree(DESK, copy)  # the same pack.json as the shipped pack, with its own class model
    raw = json.loads((copy / "data.json").read_text(encoding="utf-8"))
    raw["entities"][0]["description"] = "This copy's own class model"
    (copy / "data.json").write_text(json.dumps(raw), encoding="utf-8")
    pack = load_pack(copy)
    assert data_for(pack).entities[0].description == "This copy's own class model"
    templates()  # the systems dialog lists the shipped packs, refund-desk among them
    assert data_for(pack).entities[0].description == "This copy's own class model"
