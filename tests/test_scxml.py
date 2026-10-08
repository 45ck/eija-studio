"""SCXML export and the differential check against the kernel (ADR-0165).

The export is checked here without any engine. The differential needs python-statemachine (the `xuml` extra); without
it those tests are skipped and the gate reports NOT_RUN, never PASS. Each negative control breaks the exported chart
one way and requires the differential to find a disagreement, so a PASS is not vacuous.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from eija_studio.application.scxml import NAMESPACE, event_data, guard_condition, scxml_id, to_scxml
from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import load_pack
from eija_studio.interfaces.cli import main
from verification.scxml import differential, generate

ROOT = Path(__file__).resolve().parents[1]
PACKS = ("excursion", "library-loan", "eija-review-slice")
LOAN = load_pack(ROOT / "packs" / "library-loan")
TAG = "{" + NAMESPACE + "}"


def chart(pack=LOAN, model=None) -> ET.Element:
    parser = ET.XMLPullParser(["end"])  # our own export, parsed incrementally
    parser.feed(to_scxml(pack, model))
    return [element for _, element in parser.read_events()][-1]


def test_export_is_deterministic_and_names_its_source():
    text = to_scxml(LOAN)
    assert text == to_scxml(LOAN)
    assert LOAN.model.semantic_hash in text.splitlines()[1]


def test_every_state_and_transition_is_in_the_chart():
    root = chart()
    assert root.get("initial") == LOAN.model.initial_state
    assert [s.get("id") for s in root.iter(TAG + "state")] == list(LOAN.model.states)
    exported = {(t.get("event"), t.get("target")) for t in root.iter(TAG + "transition")}
    assert exported == {(t.action, t.to_state) for t in LOAN.model.transitions}


def test_a_transition_fires_only_from_its_source_state():
    root = chart()
    for state in root.iter(TAG + "state"):
        events = {t.get("event") for t in state.iter(TAG + "transition")}
        assert events == {t.action for t in LOAN.model.transitions if t.from_state == state.get("id")}


def test_guards_become_the_condition_and_effects_keep_their_order():
    checkout = next(t for t in LOAN.model.transitions if t.action == "CheckOut")
    assert "_event.data.assigned" in guard_condition(checkout)
    returned = next(t for t in LOAN.model.transitions if t.action == "Return")
    assert "_event.data.assigned" not in guard_condition(returned)
    element = next(t for t in chart().iter(TAG + "transition") if t.get("event") == "CheckOut")
    exprs = [a.get("expr") for a in element.iter(TAG + "assign")]
    assert exprs == ["version + 1", *(f'effects + ["{e}"]' for e in checkout.required_effects)]


def test_unknown_actor_carries_no_authority():
    assert event_data(None, 0) == {"known": False, "active": False, "role": "", "assigned": False, "expected_version": 0}


def test_names_that_are_not_plain_ids_are_escaped_one_to_one():
    assert scxml_id("OnLoan") == "OnLoan"
    odd = ["On loan", "_x", "Ölstand", "a.b", "1st"]
    ids = [scxml_id(n) for n in odd]
    assert len(set(ids)) == len(ids) and all(re.fullmatch(r"_[0-9a-f]+", i) for i in ids)


def test_refuses_a_blocked_model_and_another_packs_model():
    data = LOAN.model.model_dump(mode="json")
    data["transitions"][0]["required_effects"] = []
    with pytest.raises(DomainError) as blocked:
        to_scxml(LOAN, Workflow.model_validate(data))
    assert blocked.value.code == "POLICY_BLOCKED"
    with pytest.raises(DomainError) as other:
        to_scxml(LOAN, load_pack(ROOT / "packs" / "excursion").model)
    assert other.value.code == "WORKFLOW_PACK_MISMATCH"


def test_cli_writes_the_chart(tmp_path, capsys):
    out = tmp_path / "loan.scxml"
    assert main(["scxml", "--pack", str(ROOT / "packs" / "library-loan"), "--out", str(out)]) == 0
    assert out.read_text(encoding="utf-8") == to_scxml(LOAN)


def test_committed_charts_are_fresh():
    assert generate.main(["--check"]) == 0


def test_missing_engine_is_not_run(monkeypatch):
    monkeypatch.setattr(differential, "engine_version", lambda: None)
    report = differential.run([ROOT / "packs" / "excursion"])
    assert report["status"] == "NOT_RUN" and report["packs"] == []
    monkeypatch.setattr(differential, "run", lambda _: report)
    assert differential.main(["--pack", str(ROOT / "packs" / "excursion")]) == 3


# ---- differential (needs the engine) ---------------------------------------------------------------------------

@pytest.mark.parametrize("pack", PACKS)
def test_the_engine_agrees_with_the_kernel_on_every_case(pack):
    pytest.importorskip("statemachine.io")
    result = differential.compare(load_pack(ROOT / "packs" / pack))
    assert result["status"] == "PASS", result["disagreements"][:3]
    assert result["committed"] > 0 and result["cases"] > result["committed"]


def _mutants() -> dict[str, str]:
    text = to_scxml(LOAN)
    return {
        "role check dropped": text.replace(" and _event.data.role == &quot;Clerk&quot;", "", 1),
        "assignment check dropped": text.replace(" and _event.data.assigned", "", 1),
        "version check dropped": text.replace(" and _event.data.expected_version == version", "", 1),
        "transition retargeted": text.replace('target="Overdue"', 'target="Returned"', 1),
        "effect dropped": text.replace('<assign location="effects" expr="effects + [&quot;Notification:MemberNotified&quot;]" />', "", 1),
        "effects reordered": text.replace("Audit:LoanCheckedOut", "TMP").replace("Notification:MemberNotified", "Audit:LoanCheckedOut")
                                 .replace("TMP", "Notification:MemberNotified"),
        "version not incremented": text.replace('<assign location="version" expr="version + 1" />', "", 1),
        "initial state moved": text.replace('initial="Requested"', 'initial="OnLoan"', 1),
        "extra transition": text.replace('<state id="Returned" />',
                                         '<state id="Returned"><transition event="Cancel" target="Cancelled" /></state>', 1),
    }


@pytest.mark.parametrize("name", sorted(_mutants()))
def test_negative_control_each_broken_chart_disagrees(name):
    pytest.importorskip("statemachine.io")
    document = _mutants()[name]
    assert document != to_scxml(LOAN), "the mutant must change the chart"
    assert differential.compare(LOAN, document=document)["status"] == "FAIL"
