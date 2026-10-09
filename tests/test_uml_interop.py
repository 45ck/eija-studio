"""UML interchange (ADR-0190): faithful export to XMI, PlantUML, Mermaid and draw.io, and import through the kernel.

An export must read back as exactly the model it came from. An import never replaces the model: its state machine
becomes typed edits the kernel applies with the pack's declared guards and effects, and every element of the file is
reported as read, kept or filled in, derived, or not imported with the reason. Nothing is written or applied.
"""
from __future__ import annotations

import base64
import json
import re
import zlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from eija_studio.application.interop import FORMATS, detect_format, export_model, import_model
from eija_studio.domain.data import DataModel, data_for
from eija_studio.domain.models import DomainError
from eija_studio.domain.pack import load_pack
from eija_studio.interfaces.cli import main
from eija_studio.interfaces.http import create_app
from kernel_support import harness_studio

ROOT = Path(__file__).resolve().parents[1]
LOAN = ROOT / "packs" / "library-loan"
PACKS = sorted(p.name for p in (ROOT / "packs").iterdir() if (p / "pack.json").is_file())
SESSION = "synthetic-uml-interop-test"
HEADERS = {"Authorization": "Bearer " + SESSION, "Origin": "http://127.0.0.1:8765"}


def loan():
    pack = load_pack(LOAN)
    return pack, data_for(pack)


def unmapped(report) -> list[str]:
    return [u["element"] for u in report["unmapped"]]


@pytest.mark.parametrize("fmt", FORMATS)
@pytest.mark.parametrize("name", PACKS)
def test_every_export_reads_back_as_exactly_the_model_it_came_from(name, fmt):
    pack = load_pack(ROOT / "packs" / name)
    data = data_for(pack)
    text, report = export_model(fmt, pack, None, data)
    assert report["model"] == pack.model.semantic_hash and report["not_carried"]
    back = import_model(detect_format("x" + {"xmi": ".xmi", "plantuml": ".puml", "mermaid": ".md", "drawio": ".drawio"}[fmt], text),
                        text, pack, None, data)
    assert back["status"] == "CLEAN" and not back["defaulted"] and not back["unmapped"], back["unmapped"]
    assert back["state_machine"]["transactions"] == [] and not back["state_machine"]["changed"]
    assert back["state_machine"]["laws"] == "HOLDS" if pack.laws else True
    if data is not None:
        assert back["class_model"]["candidate"] == data.model_dump(mode="json")
    assert export_model(fmt, pack, None, data)[0] == text  # deterministic


def test_a_hand_written_plantuml_change_becomes_typed_edits_and_every_loss_is_named():
    pack, data = loan()
    text = """@startuml
[*] --> Requested
Requested --> OnLoan : CheckOut [role = Librarian]
Requested --> Cancelled : Cancel [role = Member]
OnLoan --> Overdue : MarkOverdue [role = Clerk] / Audit:Something
Overdue --> OnLoan : Renew [role = Librarian]
OnLoan --> Returned : Return [role = Librarian]
Overdue --> Returned : ReturnLate [role = Librarian and fine > 0]
OnLoan --> Lost : ReportLost [role = Librarian]
state Archive {
  state Deep
}
@enduml
@startuml
class Loan <<record>> {
  +itemTitle : String [1]
  +renewals : Integer
  +tags : String [0..*]
  +borrow() : void
}
class Member {
  +card : String [1] {maxLength = 20}
}
class Person
Member --|> Person
Loan "0..*" --> "1" Member : borrower
@enduml
"""
    report = import_model("plantuml", text, pack, None, data)
    assert report["status"] == "PARTIAL"
    machine = report["state_machine"]
    assert machine["transactions"] == [
        {"kind": "add_state", "state": "Lost"},
        {"kind": "add_transition", "id": "TR-RENEW", "action": "Renew", "from_state": "Overdue", "to_state": "OnLoan", "role": "Librarian"}]
    assert machine["policy"] == [] and machine["laws"] == "HOLDS"
    renew = next(t for t in machine["candidate"]["transitions"] if t["action"] == "Renew")
    assert renew["required_effects"] == list(pack.action("Renew").required_effects)  # the pack's, never the file's
    lost = unmapped(report)
    assert {"transition ReportLost", "composite state Archive", "Loan: +borrow() : void", "Member --|> Person",
            "ReturnLate: guard 'fine > 0'", "Loan.tags"} <= set(lost)
    kept = {d["element"]: d["reason"] for d in report["defaulted"]}
    assert "kept the pack's guards" in kept["CheckOut: guard"] and "kept the pack's" in kept["MarkOverdue: effects"]
    assert kept["Loan.renewals"] == "Integer is read as number"
    assert report["class_model"]["changes"] == {"added": ["Person"], "removed": ["Copy", "Item"], "changed": ["Loan", "Member"]}


def test_the_kernel_refuses_an_import_that_breaks_a_law_and_says_which():
    pack, data = loan()
    text, _ = export_model("plantuml", pack, None, data)
    broken = text.replace("Requested --> OnLoan : CheckOut [role = Librarian and assigned]", "Requested --> OnLoan : CheckOut [role = Member]")
    report = import_model("plantuml", broken, pack, None, data)
    assert report["status"] == "REFUSED"
    assert report["state_machine"]["transactions"] == [{"kind": "set_role", "transition": "TR-CHECKOUT", "role": "Member"}]
    assert report["state_machine"]["policy"] and report["state_machine"]["laws"] == "NOT_RUN"


def test_an_undeclared_role_or_a_missing_trigger_is_not_imported():
    pack, data = loan()
    report = import_model("mermaid", "stateDiagram-v2\n  [*] --> Requested\n  Requested --> OnLoan : CheckOut [role = Robot]\n"
                          "  Requested --> Cancelled\n", pack, None, data)
    reasons = {u["element"]: u["reason"] for u in report["unmapped"]}
    assert reasons["transition CheckOut"] == "role Robot is not declared by pack library-loan"
    assert "trigger" in reasons["Requested -> Cancelled"]
    # what the file no longer has is removed, through the kernel, and the result is judged
    assert {"kind": "remove_transition", "transition": "TR-RETURN"} in report["state_machine"]["transactions"]


def test_a_tool_written_xmi_is_read_whatever_its_namespace_version():
    pack, data = loan()
    xmi = """<?xml version="1.0"?>
<xmi:XMI xmi:version="2.1" xmlns:xmi="http://schema.omg.org/spec/XMI/2.1" xmlns:uml="http://www.omg.org/spec/UML/20110701">
 <uml:Model xmi:id="m" name="EA export">
  <packagedElement xmi:type="uml:Signal" xmi:id="sig" name="CheckOut"/>
  <packagedElement xmi:type="uml:SignalEvent" xmi:id="ev" signal="sig"/>
  <packagedElement xmi:type="uml:StateMachine" xmi:id="sm" name="Loan">
   <region xmi:type="uml:Region" xmi:id="r">
    <subvertex xmi:type="uml:Pseudostate" xmi:id="i" kind="initial"/>
    <subvertex xmi:type="uml:State" xmi:id="a" name="Requested"/>
    <subvertex xmi:type="uml:State" xmi:id="b" name="OnLoan"/>
    <subvertex xmi:type="uml:Pseudostate" xmi:id="c" kind="choice"/>
    <transition xmi:type="uml:Transition" xmi:id="t0" source="i" target="a"/>
    <transition xmi:type="uml:Transition" xmi:id="t1" source="a" target="b">
     <trigger xmi:type="uml:Trigger" xmi:id="tr" event="ev"/>
     <guard xmi:type="uml:Constraint" xmi:id="g"><specification xmi:type="uml:OpaqueExpression" xmi:id="s" body="role = Librarian"/></guard>
    </transition>
   </region>
  </packagedElement>
  <packagedElement xmi:type="uml:Class" xmi:id="L" name="Loan">
   <ownedAttribute xmi:type="uml:Property" xmi:id="p1" name="dueDate">
    <type xmi:type="uml:PrimitiveType" href="pathmap://UML_LIBRARIES/UMLPrimitiveTypes.library.uml#Date"/>
    <lowerValue xmi:type="uml:LiteralInteger" xmi:id="lv" value="1"/>
   </ownedAttribute>
   <generalization xmi:type="uml:Generalization" xmi:id="gen"/>
  </packagedElement>
 </uml:Model>
</xmi:XMI>"""
    report = import_model(detect_format("model.xmi", xmi), xmi, pack, None, data)
    assert {"choice pseudostate", "Loan generalisation"} <= set(unmapped(report))
    candidate = report["state_machine"]["candidate"]
    assert {t["action"] for t in candidate["transitions"]} == {"CheckOut"}
    [loan_class] = report["class_model"]["candidate"]["entities"]
    assert loan_class["name"] == "Loan" and [(a["name"], a["type"], a["required"]) for a in loan_class["attributes"]] == [("dueDate", "date", True)]


def test_a_compressed_drawio_page_is_read():
    pack, data = loan()
    text, _ = export_model("drawio", pack, None, data)
    page = text.split("<mxGraphModel", 1)[1].split("</mxGraphModel>", 1)[0]
    xml = "<mxGraphModel" + page + "</mxGraphModel>"
    deflate = zlib.compressobj(9, zlib.DEFLATED, -15)
    packed = base64.b64encode(deflate.compress(xml.encode()) + deflate.flush()).decode()
    report = import_model("drawio", f'<mxfile><diagram id="d" name="States">{packed}</diagram></mxfile>', pack, None, data)
    assert report["status"] == "CLEAN" and report["state_machine"]["transactions"] == []


def _packed(xml: str) -> str:
    deflate = zlib.compressobj(9, zlib.DEFLATED, -15)
    return base64.b64encode(deflate.compress(xml.encode()) + deflate.flush()).decode()


def test_a_compressed_drawio_page_gets_the_files_refusals():
    pack, data = loan()
    dtd = '<!DOCTYPE x [<!ENTITY a "aaaa">]><mxGraphModel><root>&a;</root></mxGraphModel>'
    with pytest.raises(DomainError) as error:
        import_model("drawio", f'<mxfile><diagram name="p">{_packed(dtd)}</diagram></mxfile>', pack, None, data)
    assert error.value.code == "IMPORT_INVALID"
    bomb = "<mxGraphModel><root>" + " " * 9_000_000 + "</root></mxGraphModel>"  # a few kB compressed
    with pytest.raises(DomainError) as error:
        import_model("drawio", f'<mxfile><diagram name="p">{_packed(bomb)}</diagram></mxfile>', pack, None, data)
    assert error.value.code == "IMPORT_TOO_LARGE"


@pytest.mark.parametrize("fmt", FORMATS)
def test_a_second_initial_state_is_reported_not_dropped(fmt):
    pack, data = loan()
    text, _ = export_model(fmt, pack, None, data)
    second = {"plantuml": ("[*] --> Requested", "[*] --> Requested\n[*] --> OnLoan"),
              "mermaid": ("[*] --> Requested", "[*] --> Requested\n    [*] --> OnLoan")}
    if fmt in second:
        text = text.replace(*second[fmt], 1)
    elif fmt == "xmi":  # a copy of the initial arrow, after it, pointing at OnLoan
        start = re.search(r'<transition xmi:type="uml:Transition" xmi:id="([^"]+)" source="[^"]+" target="([^"]+)" />', text)
        onloan = re.search(r'xmi:id="([^"]+)" name="OnLoan"', text).group(1)
        copy = start.group(0).replace(start.group(1), start.group(1) + "-2").replace(start.group(2), onloan)
        text = text.replace(start.group(0), start.group(0) + copy, 1)
    else:
        onloan = re.search(r'id="(state-\d+)" value="OnLoan"', text).group(1)
        arrow = f'<mxCell id="start-2" edge="1" parent="1" source="initial" target="{onloan}" style="" />'
        text = text.replace("</root>", arrow + "</root>", 1)
    report = import_model(fmt, text, pack, None, data)
    assert report["status"] == "PARTIAL" and "initial -> OnLoan" in unmapped(report), report["unmapped"]
    assert report["state_machine"]["transactions"] == []  # the first initial state is kept


@pytest.mark.parametrize("fmt", FORMATS)
def test_a_class_with_no_attributes_round_trips(fmt):
    pack, data = loan()
    doc = data.model_dump(mode="json")
    doc["entities"].append({"name": "Branch", "attributes": []})
    plain = DataModel.model_validate(doc)
    text, _ = export_model(fmt, pack, None, plain)
    back = import_model(fmt, text, pack, None, plain)
    assert back["status"] == "CLEAN", back["unmapped"]
    assert back["class_model"]["candidate"] == plain.model_dump(mode="json")


@pytest.mark.parametrize("fmt", ["xmi", "drawio"])
def test_xml_with_a_dtd_is_refused_before_parsing(fmt):
    pack, data = loan()
    bomb = '<?xml version="1.0"?><!DOCTYPE x [<!ENTITY a "aaaa">]><x>&a;</x>'
    with pytest.raises(DomainError) as error:
        import_model(fmt, bomb, pack, None, data)
    assert error.value.code == "IMPORT_INVALID"


def test_format_detection():
    assert detect_format("a.puml", "x") == "plantuml"
    assert detect_format("", "<mxfile><diagram/></mxfile>") == "drawio"
    assert detect_format("a.xml", "<mxfile/>") == "drawio"
    assert detect_format("", "classDiagram\n class A") == "mermaid"
    with pytest.raises(DomainError):
        detect_format("notes.txt", "hello")


def test_cli_export_then_import_is_clean_and_writes_candidates(tmp_path, capsys):
    out = tmp_path / "loan.xmi"
    assert main(["uml", "export", "--format", "xmi", "--pack", str(LOAN), "--out", str(out)]) == 0
    capsys.readouterr()
    assert main(["uml", "import", str(out), "--pack", str(LOAN), "--out-dir", str(tmp_path / "c")]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "CLEAN"
    assert json.loads((tmp_path / "c" / "workflow.json").read_text())["id"] == "library-loan"
    assert (tmp_path / "c" / "data.json").is_file()


def test_http_export_and_import_save_nothing(tmp_path):
    studio = harness_studio(tmp_path / "workspace", pack=LOAN)
    app = create_app(studio, SESSION)
    client = TestClient(app, base_url=HEADERS["Origin"])
    with studio.store.transaction() as u:
        before = u.active()["model"]
    exported = client.post("/api/play/export", json={"format": "plantuml"}, headers=HEADERS).json()
    assert exported["filename"] == "library-loan.puml" and "@startuml" in exported["text"]
    edited = exported["text"].replace("Overdue --> Returned", "Overdue --> OnLoan : Renew [role = Librarian]\nOverdue --> Returned")
    report = client.post("/api/play/import", json={"filename": "x.puml", "text": edited}, headers=HEADERS).json()
    assert report["status"] == "CLEAN" and [t["kind"] for t in report["state_machine"]["transactions"]] == ["add_transition"]
    with studio.store.transaction() as u:
        assert u.active()["model"] == before
    app.state.play.stop()
