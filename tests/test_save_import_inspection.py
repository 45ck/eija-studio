"""Regression tests for the defects the 2026-11-13 inspection of saving and UML import found (ADR-0245).

Each test names the defect it pins. The import ones are about partial reads: a file PlayIDE reads only in part must
never turn into a plan or a class model that removes what the file still has (issue #165). The save ones are about a
tab that shows another system than the one the server serves now.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from eija_studio.application.interop import export_model, import_model
from eija_studio.domain.data import load_data
from eija_studio.domain.pack import PACKS_ROOT, load_pack
from test_play_systems import HEADERS, SKETCH, post, served  # noqa: F401  (the served fixture)

LOAN = PACKS_ROOT / "library-loan"
CANCEL = "Requested --> Cancelled : Cancel [role = Member] / Audit:LoanCancelled"


@pytest.fixture(scope="module")
def loan():
    pack = load_pack(LOAN)
    return pack, load_data(LOAN, pack.id)


def _swap(text: str, old: str, new: str) -> str:
    assert text.count(old) == 1, old
    return text.replace(old, new)


def _removals(report) -> list[dict]:
    return [t for t in report["state_machine"]["transactions"] if t["kind"].startswith("remove")]


# ---- D1: an arrow the reader cannot read made the import remove that transition ----------------------------------

@pytest.mark.parametrize("arrow", ["->>", "-[#red]-[bold]>"])
@pytest.mark.parametrize("fmt", ["plantuml", "mermaid"])
def test_an_unreadable_arrow_makes_the_read_partial_so_nothing_is_removed(loan, fmt, arrow):
    pack, data = loan
    text = _swap(export_model(fmt, pack, data=data)[0], CANCEL, CANCEL.replace("-->", arrow))
    report = import_model(fmt, text, pack, data=data)
    assert report["status"] == "PARTIAL" and _removals(report) == []
    assert any(u["element"].startswith("Requested") and "arrow" in u["reason"] for u in report["unmapped"])
    assert any(u["element"] == "removing transition Cancel" for u in report["unmapped"])


@pytest.mark.parametrize("line", ["Requested -left[#red]-> Cancelled : Cancel [role = Member] / Audit:LoanCancelled",
                                  "Cancelled <-- Requested : Cancel [role = Member] / Audit:LoanCancelled"])
def test_plantuml_arrow_styles_after_the_direction_and_backward_arrows_are_read(loan, line):
    pack, data = loan
    text = _swap(export_model("plantuml", pack, data=data)[0], CANCEL, line)
    report = import_model("plantuml", text, pack, data=data)
    assert report["status"] == "CLEAN" and report["state_machine"]["transactions"] == []


# ---- D8: a <<choice>> pseudostate became a state, and the plan retargeted a transition to it ---------------------

@pytest.mark.parametrize("fmt", ["plantuml", "mermaid"])
@pytest.mark.parametrize("declared_first", [True, False])
def test_a_pseudostate_is_never_read_as_a_state(loan, fmt, declared_first):
    pack, data = loan
    through = ["Requested --> pick : Cancel [role = Member] / Audit:LoanCancelled", "pick --> Cancelled"]
    lines = ["state pick <<choice>>", *through] if declared_first else [*through, "state pick <<choice>>"]
    text = _swap(export_model(fmt, pack, data=data)[0], CANCEL, "\n".join(lines))
    report = import_model(fmt, text, pack, data=data)
    assert report["state_machine"]["transactions"] == []  # no add_state pick, no retarget, no removal
    assert "pick" not in report["state_machine"]["candidate"]["states"]
    assert sum("pseudostate pick" in u["reason"] for u in report["unmapped"]) == 2


def test_an_xmi_transition_to_a_choice_pseudostate_makes_the_read_partial(loan):
    pack, data = loan
    text = export_model("xmi", pack, data=data)[0]
    text = _swap(text, '<subvertex xmi:type="uml:State" xmi:id="state.Cancelled" name="Cancelled" />',
                 '<subvertex xmi:type="uml:State" xmi:id="state.Cancelled" name="Cancelled" />'
                 '<subvertex xmi:type="uml:Pseudostate" xmi:id="pick" kind="choice" />')
    text = _swap(text, 'source="state.Requested" target="state.Cancelled"', 'source="state.Requested" target="pick"')
    report = import_model("xmi", text, pack, data=data)
    assert _removals(report) == [] and report["status"] == "PARTIAL"


def test_a_labelled_drawio_connector_to_a_rhombus_makes_the_read_partial(loan):
    pack, data = loan
    text = export_model("drawio", pack, data=data)[0]
    rhombus = '<mxCell style="rhombus;whiteSpace=wrap;html=1;" vertex="1" parent="1" id="pick" value=""><mxGeometry as="geometry" /></mxCell>'
    text = _swap(text, 'source="state-0" target="state-4">', 'source="state-0" target="pick">')
    text = text.replace("</root>", rhombus + "</root>", 1)
    report = import_model("drawio", text, pack, data=data)
    assert _removals(report) == [] and report["status"] == "PARTIAL"


# ---- D2 and D3: a partial class read dropped attributes and associations, and the summary missed associations ----

def test_an_unreadable_attribute_or_association_is_kept_not_deleted(loan):
    pack, data = loan
    text = export_model("plantuml", pack, data=data)[0]
    text = _swap(text, "+itemTitle : String [1] {maxLength = 200}", "+itemTitle : Money [1]")
    text = _swap(text, 'Item "1" *-- "1..*" Copy : copies', 'Item "1" *-- "2..5" Copy : copies')
    report = import_model("plantuml", text, pack, data=data)
    cm = report["class_model"]
    assert report["status"] == "PARTIAL" and cm["changed"] is False  # what was not read is kept as it is
    loan_class = next(e for e in cm["candidate"]["entities"] if e["name"] == "Loan")
    assert loan_class["attributes"][0]["name"] == "itemTitle"  # in its place
    assert len(cm["candidate"]["associations"]) == len(data.associations)
    kept = [d["element"] for d in report["defaulted"] if d["reason"].startswith("kept as the current model has it")]
    assert kept == ["Loan.itemTitle", "composition Item -> Copy"]


def test_the_class_model_changes_name_associations(loan):
    pack, data = loan
    text = _swap(export_model("plantuml", pack, data=data)[0], 'Loan "0..*" --> "1" Copy : copy', "")
    cm = import_model("plantuml", text, pack, data=data)["class_model"]
    assert cm["changed"] is True and cm["changes"]["changed"] == []
    assert cm["changes"]["associations"] == {"added": [], "removed": ["Loan -> Copy (copy)"], "changed": []}


# ---- D4: a tab left on another system saved its work over this system's draft -------------------------------------

def test_a_save_from_a_page_on_another_system_is_refused(served):  # noqa: F811
    client, systems, _tmp = served
    loan_pack = systems.current["pack"]
    step = {"kind": "add_state", "state": "Archived"}
    assert post(client, "/api/play/draft", {"steps": [{"transaction": step}], "pack": loan_pack}).status_code == 200
    post(client, "/api/play/systems/new", {"name": "Support desk", "record": "Ticket", "sketch": SKETCH})
    desk = systems.current["pack"]
    assert post(client, "/api/play/draft", {"steps": [{"transaction": {"kind": "add_state", "state": "Held"}}], "pack": desk}).status_code == 200
    # The tab still showing library-loan saves and clears: both are refused, and the desk's draft is untouched.
    stale = post(client, "/api/play/draft", {"steps": [{"transaction": step}], "pack": loan_pack})
    assert stale.status_code == 409 and stale.json()["code"] == "SYSTEM_CHANGED"
    assert post(client, "/api/play/draft/clear", {"pack": loan_pack}).status_code == 409
    draft = client.get("/api/play/draft", headers=HEADERS).json()["draft"]
    assert draft["steps"][0]["transaction"]["state"] == "Held" and "pack" not in draft
    post(client, "/api/play/systems/open", {"pack": loan_pack})
    assert client.get("/api/play/draft", headers=HEADERS).json()["draft"]["steps"][0]["transaction"] == step


def test_the_page_names_its_system_when_it_saves():
    script = (Path(__file__).parents[1] / "src/eija_studio/resources/web/play-systems.js").read_text(encoding="utf-8")
    assert "pack: opened" in script and 'P.api("/api/play/draft/clear", { ...(opened ? { pack: opened } : {}), base: revision })' in script


# ---- D9: reasons still said value guards and composite states were planned, after both shipped ---------------------

def test_reasons_do_not_call_shipped_kernel_features_planned(loan):
    pack, data = loan
    text = export_model("plantuml", pack, data=data)[0]
    text = _swap(text, "Cancel [role = Member]", "Cancel [role = Member and fine > 0]") + "\n@startuml\nstate Archive {\n  state Deep\n}\n@enduml\n"
    reasons = " ".join(u["reason"] for u in import_model("plantuml", text, pack, data=data)["unmapped"])
    assert "planned" not in reasons and "ADR-0234" in reasons and "ADR-0240" in reasons
