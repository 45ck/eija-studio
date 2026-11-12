"""Composite states (issue #93 item 3, ADR-0238).

A workflow may group states into UML composite states, nested to any depth, each with the child a transition into it
enters first. A record is always in one plain state and the kernel runs the flat machine, so a composite never changes
what a step does. The SCXML chart nests the states and carries an action that leaves every state of a composite once,
on the composite; the differential checks the engine's hierarchy against the kernel. Flat models keep their bytes.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from eija_studio.application.diagram_emitters import emit
from eija_studio.application.diagrams import diff_summary, state_graph
from eija_studio.application.law_proof import prove_laws, with_laws
from eija_studio.application.scxml import hoisted, to_scxml
from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import load_pack
from eija_studio.domain.transactions import RemoveState, RenameState, apply_structural

ROOT = Path(__file__).resolve().parents[1]
DESK = load_pack(ROOT / "packs" / "refund-desk")
# The refund desk lets a customer withdraw only a new request; without that law, Withdraw may leave other states too.
LOOSE = with_laws(DESK, [law.model_dump(mode="json") for law in DESK.laws if law.id != "withdraw-before-triage"])
OPEN = {"name": "Open", "states": ["Requested", "Assessed", "Deciding"], "initial": "Requested"}


def grouped(model: Workflow, composites: list[dict], extra: list[dict] | None = None) -> Workflow:
    raw = model.model_dump(mode="json")
    raw["composites"] = composites
    raw["transitions"] += extra or []
    return Workflow.model_validate(raw)


def withdraw_from(state: str) -> dict:
    """Withdraw from another state: the same transition but for its id and source (ADR-0232)."""
    template = next(t for t in DESK.model.model_dump(mode="json")["transitions"] if t["action"] == "Withdraw")
    return dict(template, id=f"TR-WITHDRAW-{state.upper()}", from_state=state)


def _never_built(*_: object) -> None:
    raise AssertionError("no transition is declared by these edits")


def test_the_refund_desk_groups_its_states_and_flat_models_keep_their_bytes():
    model = DESK.model
    assert [c.name for c in model.composites] == ["Deciding", "PayingOut"]
    assert model.leaves("Deciding") == ("AwaitingApproval", "WithSupervisor") and model.entry("PayingOut") == "Approved"
    assert model.parent("WithSupervisor") == "Deciding" and model.parent("Paid") is None
    for pack_dir in sorted(p for p in (ROOT / "packs").iterdir() if (p / "pack.json").is_file() and p.name != "refund-desk"):
        raw = json.loads((pack_dir / "pack.json").read_text(encoding="utf-8"))["model"]
        assert "composites" not in json.dumps(Workflow.model_validate(raw).model_dump(mode="json")), pack_dir.name
    shuffled = grouped(model, [{"name": "Deciding", "states": ["WithSupervisor", "AwaitingApproval"], "initial": "AwaitingApproval"},
                               {"name": "PayingOut", "states": ["Approved", "PayoutFailed"], "initial": "Approved"}][::-1])
    assert shuffled.semantic_hash == model.semantic_hash  # groups and their children are sets


def test_nesting_is_a_tree_over_the_states():
    nested = grouped(DESK.model, [*[c.model_dump() for c in DESK.model.composites], OPEN])
    assert nested.ancestors("WithSupervisor") == ("Deciding", "Open") and nested.entry("Open") == "Requested"
    assert nested.leaves("Open") == ("Requested", "Assessed", "AwaitingApproval", "WithSupervisor")
    deciding = {"name": "Deciding", "states": ["AwaitingApproval", "WithSupervisor"], "initial": "AwaitingApproval"}
    broken = [
        [deciding, dict(deciding)],  # two composites share a name
        [{"name": "Paid", "states": ["Approved"], "initial": "Approved"}],  # a composite named like a state
        [deciding, {"name": "Twice", "states": ["WithSupervisor"], "initial": "WithSupervisor"}],  # two parents
        [{"name": "Ghost", "states": ["Nowhere"], "initial": "Nowhere"}],  # an unknown child
        [{"name": "Lost", "states": ["Paid"], "initial": "Declined"}],  # an initial that is not a child
        [{"name": "A", "states": ["B"], "initial": "B"}, {"name": "B", "states": ["A"], "initial": "A"}],  # a cycle
    ]
    for composites in broken:
        with pytest.raises(ValueError, match="tree"):
            grouped(DESK.model, composites)


def test_the_kernel_runs_the_flat_machine():
    """Grouping changes no transition, so the law proof finds the same runs."""
    flat = Workflow.model_validate(DESK.model.model_dump(mode="json", exclude={"composites"}))
    assert flat.transitions == DESK.model.transitions
    grouped_report, flat_report = prove_laws(DESK), prove_laws(DESK, flat)
    assert grouped_report["search"] == flat_report["search"]
    assert [v["status"] for v in grouped_report["laws"]] == [v["status"] for v in flat_report["laws"]]


def test_scxml_nests_the_states_and_carries_a_shared_action_on_the_composite():
    chart = to_scxml(DESK)
    assert '<state id="Deciding" initial="AwaitingApproval">' in chart
    model = grouped(DESK.model, [*[c.model_dump() for c in DESK.model.composites], OPEN],
                    [withdraw_from("Assessed"), withdraw_from("AwaitingApproval"), withdraw_from("WithSupervisor")])
    carried = hoisted(model)
    assert [t.action for t in carried["Open"]] == ["Withdraw"]  # it leaves every state of Open, so Open carries it once
    assert all(t.action != "Withdraw" for name in ("Requested", "Assessed", "Deciding", "AwaitingApproval") for t in carried.get(name, []))
    partly = grouped(DESK.model, [c.model_dump() for c in DESK.model.composites], [withdraw_from("AwaitingApproval")])
    assert [t.from_state for t in hoisted(partly)["AwaitingApproval"] if t.action == "Withdraw"] == ["AwaitingApproval"]
    differential = pytest.importorskip("verification.scxml.differential")
    if differential.load is None:
        pytest.skip("python-statemachine is not installed")
    assert differential.compare(DESK)["status"] == "PASS"
    report = differential.compare(LOOSE, model)
    assert report["status"] == "PASS", report["disagreements"][:3]
    # Negative control: carry Withdraw on the inner composite only, and the engine no longer withdraws from Requested.
    text = to_scxml(LOOSE, model)
    start = text.index('<transition event="Withdraw"')
    withdraw = text[start:text.index("</transition>", start) + len("</transition>")]
    moved = text.replace(withdraw, "", 1).replace('<state id="Deciding" initial="AwaitingApproval">',
                                                  '<state id="Deciding" initial="AwaitingApproval">' + withdraw, 1)
    assert differential.compare(LOOSE, model, moved)["status"] == "FAIL"


def test_diagrams_draw_composites_as_boxes_and_the_diff_reports_regrouping():
    graph = state_graph(DESK.model)
    assert {(c.id, c.parent) for c in graph.clusters} == {("Deciding", None), ("PayingOut", None)}
    assert {n.id: n.cluster for n in graph.nodes}["WithSupervisor"] == "Deciding"
    mermaid = emit(graph, "mermaid")
    assert "    state Deciding {\n        AwaitingApproval\n        WithSupervisor\n    }" in mermaid
    assert 'state "Deciding" as Deciding {' in emit(graph, "plantuml")
    assert 'subgraph "cluster_Deciding"' in emit(graph, "dot")
    nested = grouped(DESK.model, [*[c.model_dump() for c in DESK.model.composites], OPEN])
    assert "        state Deciding {" in emit(state_graph(nested), "mermaid")  # nested inside Open
    assert diff_summary(DESK.model, nested)["composites"] == {"added": ["Open"], "removed": [], "changed": []}
    assert "composites" not in diff_summary(DESK.model, DESK.model)


def test_editing_states_keeps_the_composites_coherent():
    renamed = apply_structural(DESK.model, RenameState(kind="rename_state", state="WithSupervisor", to="Escalated"), _never_built)
    assert renamed.composite("Deciding").states == ("AwaitingApproval", "Escalated")
    raw = DESK.model.model_dump(mode="json")
    raw["states"].append("Parked")
    raw["composites"][0]["states"].append("Parked")
    parked = Workflow.model_validate(raw)
    removed = apply_structural(parked, RemoveState(kind="remove_state", state="Parked"), _never_built)
    assert removed.composite("Deciding").states == ("AwaitingApproval", "WithSupervisor")
    with pytest.raises(DomainError) as e:  # Approved starts PayingOut, and transitions use it
        apply_structural(DESK.model, RemoveState(kind="remove_state", state="Approved"), _never_built)
    assert "composite:PayingOut" in e.value.details["refs"]
