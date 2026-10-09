"""Actors that are not people in UML interchange (ADR-0210 with ADR-0190): «agent», «timer» and «system» are written
on export and read back on import, and an import never changes a role's kind."""
from __future__ import annotations

import pytest

from eija_studio.application.interop import FORMATS, export_model, import_model, parse_file, start_from_file
from eija_studio.domain.data import data_for
from eija_studio.domain.pack import PACKS_ROOT, load_pack, parse_pack

REFUNDS = load_pack(PACKS_ROOT / "refund-desk")
KINDS = {r.id: r.kind for r in REFUNDS.roles}
DRAWN = ("xmi", "plantuml", "drawio")  # the formats with a use case diagram


def test_the_example_pack_has_every_kind():
    assert set(KINDS.values()) == {"human", "agent", "timer", "system"}


@pytest.mark.parametrize("fmt", DRAWN)
def test_each_kind_round_trips(fmt):
    text, _ = export_model(fmt, REFUNDS, None, data_for(REFUNDS))
    assert {name: kind for name, (kind, _) in parse_file(fmt, text).actors.items()} == KINDS
    report = import_model(fmt, text, REFUNDS, None, data_for(REFUNDS))
    assert report["status"] == "CLEAN" and "actor SupportAgent («agent»)" in {m["element"] for m in report["mapped"]}
    documents, started = start_from_file(fmt, text, "Refunds", "refunds")
    assert {r.id: r.kind for r in parse_pack(documents["pack.json"]).roles} == KINDS
    assert started["status"] == "CLEAN" and not [d for d in started["defaulted"] if "kind" in d["element"]]


def test_mermaid_has_no_actors_and_says_so():
    text, exported = export_model("mermaid", REFUNDS, None, data_for(REFUNDS))
    assert any("SupportAgent «agent»" in x for x in exported["not_carried"])
    documents, started = start_from_file("mermaid", text, "Refunds", "refunds")
    assert all(r.kind == "human" for r in parse_pack(documents["pack.json"]).roles)
    assert {"element": "role kinds", "where": "use case diagram",
            "reason": "the file draws no actors; every role is a person"} in started["defaulted"]


@pytest.mark.parametrize("name", sorted(p.name for p in PACKS_ROOT.iterdir() if (p / "pack.json").is_file()))
def test_a_pack_of_people_exports_as_before(name):
    pack = load_pack(PACKS_ROOT / name)
    if any(r.kind != "human" for r in pack.roles):
        pytest.skip("this pack has actors that are not people")
    for fmt in FORMATS:
        text, report = export_model(fmt, pack, None, data_for(pack))
        assert not any(k in text for k in ("profileApplication", "<<agent", "&laquo;agent", "base_Actor"))
        assert not any("kinds of actor" in x for x in report["not_carried"])


def test_an_import_reports_a_different_kind_and_never_changes_it():
    text, _ = export_model("plantuml", REFUNDS, None, data_for(REFUNDS))
    drawn_as_person = text.replace(" <<agent>>", "")
    report = import_model("plantuml", drawn_as_person, REFUNDS, None, data_for(REFUNDS))
    lost = {u["element"]: u["reason"] for u in report["unmapped"]}
    assert "the file draws a person; the pack declares «agent»" in lost["actor SupportAgent kind"]
    assert report["status"] == "PARTIAL" and REFUNDS.role_kind("SupportAgent") == "agent"


HAND_PLANTUML = """@startuml
Open --> Done : Close [role = Bot]
Open --> Late : Expire [role = Clock]
Open --> Paid : Pay [role = Bank]
Open --> Seen : Look [role = Clerk]
@enduml
@startuml
:Bot: <<agent>>
actor "Clock" as C <<timer>>
actor Bank <<System>>
actor Clerk <<actor>>
actor Robot <<robot>>
actor "Help desk" <<agent>>
@enduml
"""
HAND_XMI = """<?xml version="1.0"?>
<xmi:XMI xmlns:xmi="http://www.omg.org/spec/XMI/20110701" xmlns:uml="http://www.omg.org/spec/UML/20110701"
         xmlns:Custom="http://example.com/profile">
  <uml:Model xmi:id="m" name="M">
    <packagedElement xmi:type="uml:StateMachine" xmi:id="sm" name="SM">
      <region xmi:id="r">
        <subvertex xmi:type="uml:Pseudostate" xmi:id="i"/>
        <subvertex xmi:type="uml:State" xmi:id="a" name="Open"/>
        <subvertex xmi:type="uml:State" xmi:id="b" name="Done"/>
        <transition xmi:id="t0" source="i" target="a"/>
        <transition xmi:id="t1" source="a" target="b" name="Close">
          <trigger xmi:id="tr" name="Close"/>
          <guard xmi:id="g"><specification xmi:type="uml:OpaqueExpression" xmi:id="s"><body>role = Bot</body></specification></guard>
        </transition>
      </region>
    </packagedElement>
    <packagedElement xmi:type="uml:Actor" xmi:id="EAID_1" name="Bot"/>
  </uml:Model>
  <Custom:Agent xmi:id="x"><base_Actor xmi:idref="EAID_1"/></Custom:Agent>
</xmi:XMI>
"""
HAND_DRAWIO = """<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>
<mxCell id="a" value="&#171;system&#187;&lt;br&gt;Bank" style="rounded=0;html=1;" vertex="1" parent="1"/>
<mxCell id="b" value="Clerk" style="shape=umlActor;html=1;" vertex="1" parent="1"/>
</root></mxGraphModel>"""


def test_hand_written_files_read_each_kind():
    parsed = parse_file("plantuml", HAND_PLANTUML)
    assert {n: k for n, (k, _) in parsed.actors.items()} == {"Bot": "agent", "Clock": "timer", "Bank": "system",
                                                            "Clerk": "human", "Robot": "human",
                                                            "Help desk": "agent"}
    assert any(s["element"] == "actor Robot <<robot>>" for s in parsed.skipped)  # an unknown kind is named, not guessed
    documents, report = start_from_file("plantuml", HAND_PLANTUML, "Desk", "desk")
    assert {r.id: r.kind for r in parse_pack(documents["pack.json"]).roles} == {
        "Bot": "agent", "Clock": "timer", "Bank": "system", "Clerk": "human", "Robot": "human"}  # Robot performs nothing yet
    assert "is not a name" in {u["element"]: u["reason"] for u in report["unmapped"]}["actor Help desk"]
    assert {n: k for n, (k, _) in parse_file("xmi", HAND_XMI).actors.items()} == {"Bot": "agent"}
    assert {n: k for n, (k, _) in parse_file("drawio", HAND_DRAWIO).actors.items()} == {"Bank": "system", "Clerk": "human"}
