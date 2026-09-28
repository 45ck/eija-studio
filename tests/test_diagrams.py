"""Diagrams are generated projections of the executable model (ADR-0019, ADR-0023).

Golden files pin the text; the other tests are negative controls that would fail if a diagram were
hand-drawn, order-dependent, or disagreed with what the runtime actually does. Regenerate goldens with
`EIJA_UPDATE_GOLDEN=1 python -m pytest tests/test_diagrams.py` and review the diff.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import BaseModel

from eija_studio.application import diagrams
from eija_studio.application.diagram_catalog import VIEW_FORMATS, case_diagrams, demo_pair, docs_bundle, render_view
from eija_studio.application.diagram_emitters import emit, safe_ids
from eija_studio.application.diagrams import class_model, commit_sequence, diff_graph, diff_summary, impact_graph, state_graph
from eija_studio.domain.impact import model_impact
from eija_studio.domain.models import DomainError, ExecuteCommand, Workflow
from eija_studio.domain.policy import baseline

GOLDEN = Path(__file__).parent / "golden"
EXT = {"mermaid": "mmd", "plantuml": "puml", "dot": "dot"}
BEFORE, AFTER = demo_pair()


def golden_cases():
    cases = []
    for fmt in EXT:
        for view in ("state-baseline", "state-candidate", "diff", "impact", "journey", "class"):
            if fmt in VIEW_FORMATS[view.split("-")[0]]:
                cases.append((view, fmt, None))
        if fmt in VIEW_FORMATS["sequence"]:
            cases += [("sequence-" + t.action.lower(), fmt, t.action) for t in AFTER.transitions]
    return cases


def generate(view: str, fmt: str, action: str | None, before=BEFORE, after=AFTER) -> str:
    if view == "state-baseline":
        return render_view("state", fmt, before)
    if view == "state-candidate":
        return render_view("state", fmt, before, after)
    return render_view(view.split("-")[0], fmt, before, after, action)


@pytest.mark.parametrize("view,fmt,action", golden_cases())
def test_golden_text_is_pinned(view, fmt, action):
    path = GOLDEN / f"{view}.{EXT[fmt]}"
    text = generate(view, fmt, action)
    if os.environ.get("EIJA_UPDATE_GOLDEN"):
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
    assert path.read_bytes() == text.encode("utf-8"), f"{path.name} drifted; review then EIJA_UPDATE_GOLDEN=1"
    assert "\r" not in text and text.endswith("\n") and not text.endswith("\n\n")


def reordered(wf: Workflow) -> Workflow:
    data = wf.model_dump(mode="json")
    data["states"] = list(reversed(data["states"]))
    data["transitions"] = list(reversed(data["transitions"]))
    for t in data["transitions"]:
        for key in ("guards", "required_effects", "forbidden_effects"):
            t[key] = list(reversed(t[key]))
    return Workflow.model_validate(data)


@pytest.mark.parametrize("view,fmt,action", golden_cases())
def test_reordering_the_definition_does_not_change_output(view, fmt, action):
    assert reordered(AFTER).model_dump() != AFTER.model_dump()  # the control really differs
    assert reordered(AFTER).semantic_hash == AFTER.semantic_hash
    assert generate(view, fmt, action, reordered(BEFORE), reordered(AFTER)) == generate(view, fmt, action)


def test_docs_diagrams_equal_regeneration():
    docs = Path(__file__).parents[1] / "docs" / "diagrams"
    bundle = docs_bundle()
    assert {p.name for p in docs.iterdir()} == set(bundle)
    for name, text in bundle.items():
        assert (docs / name).read_bytes() == text.encode("utf-8"), name


def mermaid_edges(text: str) -> set[tuple[str, str, str]]:
    """Independent reader of the emitted text: (source, target, action) of each state-diagram edge."""
    found = set()
    for m in re.finditer(r"^\s+(\w+) --> (\w+): (?:[+~-] )?(\w+) · ", text, re.M):
        found.add((m.group(1), m.group(2), m.group(3)))
    return found


def test_state_diagram_contains_exactly_the_workflow_transitions():
    for wf in (BEFORE, AFTER):
        text = render_view("state", "mermaid", wf)
        assert mermaid_edges(text) == {(t.from_state, t.to_state, t.action) for t in wf.transitions}
        for state in wf.states:
            assert re.search(rf"\b{state}\b", text)


def test_a_changed_rule_changes_the_picture():
    data = AFTER.model_dump(mode="json")
    for t in data["transitions"]:
        if t["action"] == "Approve":
            t["role"] = "Teacher"  # authority change: same edge, different role
    mutated = Workflow.model_validate(data)
    assert render_view("state", "mermaid", mutated) != render_view("state", "mermaid", AFTER)
    text = render_view("diff", "mermaid", AFTER, mutated)
    assert "~ Approve · Teacher" in text and "class Approved,Recommended changed" in text
    assert diff_summary(AFTER, mutated)["changed_actions"] == {"Approve": [{"field": "role", "before": "Registrar", "after": "Teacher"}]}


def test_diff_marks_added_removed_and_changed():
    g = diff_graph(BEFORE, AFTER)
    by_label = {e.label.lstrip("+-~ ").split(" · ")[0] + ":" + e.status for e in g.edges}
    assert {"Recommend:added", "Approve:added", "Reject:added", "Approve:removed", "Reject:removed"} <= by_label
    assert {n.id: n.status for n in g.nodes}["Recommended"] == "added" and {n.id: n.status for n in g.nodes}["Draft"] == "same"
    assert {s for s, _ in g.legend} == {"added", "removed", "changed", "same"}
    reverse = diff_graph(AFTER, BEFORE)
    assert {n.id: n.status for n in reverse.nodes}["Recommended"] == "removed"


def test_identical_models_have_an_empty_diff():
    g = diff_graph(BEFORE, BEFORE)
    assert {n.status for n in g.nodes} == {"same"} and {e.status for e in g.edges} == {"same"} and g.legend == ()
    text = render_view("diff", "mermaid", BEFORE, BEFORE)
    assert "classDef" not in text and "legend_" not in text
    assert diff_summary(BEFORE, BEFORE) == {"added_states": [], "removed_states": [], "added_actions": [], "removed_actions": [], "changed_actions": {}}


def test_impact_highlight_equals_model_impact():
    report = model_impact(BEFORE, AFTER)
    g = impact_graph(BEFORE, AFTER)
    marked = {n.id for n in g.nodes if n.status in {"changed", "affected"}}
    assert marked == set(report["affected"]) and {n.id for n in g.nodes if n.status == "changed"} == {"rule:" + a for a in report["changed_actions"]}
    quiet = impact_graph(BEFORE, BEFORE)
    assert {n.status for n in quiet.nodes} == {"same"} and not any(w in emit(quiet, "mermaid") for w in ("linkStyle", "\n    class ", "classDef"))


def test_sequence_failure_codes_are_the_codes_the_runtime_raises(studio, selected):
    """The picture lists guard failures; each must be a real, reachable runtime outcome."""
    def run(state, actor, action, **changes):
        item = studio.reset_preview(selected["id"], selected["version"], state)
        cmd = ExecuteCommand.model_validate({"operation_id": uuid4().hex, "instance_id": item["id"], "actor_id": actor,
                                             "action": action, "expected_version": item["version"]} | changes)
        with pytest.raises(DomainError) as e:
            studio.execute(selected["id"], cmd)
        return e.value.code
    raised = {run("Submitted", "teacher-revoked", "Recommend"), run("Submitted", "viewer", "Recommend"),
              run("Submitted", "teacher-unassigned", "Recommend"), run("Submitted", "teacher-assigned", "Recommend", expected_version=9),
              run("Draft", "teacher-assigned", "Recommend")}
    text = render_view("sequence", "mermaid", BEFORE, AFTER, "Recommend")
    drawn = set(re.findall(r"\b([A-Z]+_[A-Z]+)\b", text)) - {"ONE_TRANSACTION"}
    assert raised == {"ACTOR_REVOKED", "ROLE_DENIED", "ASSIGNMENT_DENIED", "STALE_VERSION", "STATE_DENIED"}
    assert drawn == raised | {"OPERATION_CONFLICT"}
    # Approve has no assignment guard: not drawn, and the runtime never raises it for an unassigned registrar.
    assert "ASSIGNMENT_DENIED" not in render_view("sequence", "mermaid", BEFORE, AFTER, "Approve")
    item = studio.reset_preview(selected["id"], selected["version"], "Recommended")
    result = studio.execute(selected["id"], ExecuteCommand(operation_id=uuid4().hex, instance_id=item["id"], actor_id="registrar",
                                                           action="Approve", expected_version=item["version"]))
    assert result["committed"]


def test_sequence_order_is_the_runtime_order_and_effects_come_from_the_transition():
    text = render_view("sequence", "mermaid", BEFORE, AFTER, "Recommend")
    order = ["load actor", "authorise BEFORE replay", "ROLE_DENIED", "find operation", "OPERATION_CONFLICT", "STALE_VERSION",
             "STATE_DENIED", "compare-and-set", "Audit:ExcursionRecommended", "Notification:RegistrarQueued", "record operation", "ONE transaction"]
    assert [text.index(x) for x in order] == sorted(text.index(x) for x in order)
    assert "participant Outbox" in text and "Notification" not in render_view("sequence", "mermaid", BEFORE, AFTER, "Approve")
    assert "participant Outbox" not in render_view("sequence", "mermaid", BEFORE, AFTER, "Approve")
    with pytest.raises(DomainError) as e:
        commit_sequence(AFTER, "Teleport")
    assert e.value.code == "ACTION_DENIED"


def test_class_diagram_is_introspected_not_listed(monkeypatch):
    class Probe(BaseModel):
        secret_new_field: int
        child: diagrams.Transition

    monkeypatch.setattr(diagrams, "CONTRACTS", (*diagrams.CONTRACTS, Probe))
    text = emit(class_model(), "mermaid")
    assert "class Probe" in text and "+int secret_new_field" in text and 'Probe "1" *-- "1" Transition : child' in text
    monkeypatch.undo()
    assert "Probe" not in emit(class_model(), "mermaid")


def test_class_diagram_covers_every_field_and_relation_of_the_real_contracts():
    model = class_model()
    names = {c.name for c in model.classes}
    for contract in diagrams.CONTRACTS:
        assert contract.__name__ in names
        node = next(c for c in model.classes if c.name == contract.__name__)
        related = {r.label for r in model.relations if r.source == contract.__name__}
        assert set(contract.model_fields) == {m.name for m in node.members} | related
    assert any(r.source == "Workflow" and r.target == "Transition" and r.multiplicity == "1..*" for r in model.relations)
    assert any(r.source == "ChangeCase" and r.label == "candidate" and r.multiplicity == "0..1" for r in model.relations)
    assert set(diagrams.DDD_ROLE) <= {c.__name__ for c in diagrams.CONTRACTS}


def hostile() -> Workflow:
    guards = ["actor_active", "role_current", "state_equals", "expected_version", "operation_binding"]
    def t(i, a, f, to, role):
        return {"id": i, "action": a, "from_state": f, "to_state": to, "role": role, "guards": guards,
                "required_effects": ["Audit:X"], "forbidden_effects": []}
    return Workflow.model_validate({"initial_state": "start", "states": ["start", "end", 'a "q" <b>x</b>', "semi;colon #h"],
        "transitions": [t("T-1", "Go", "start", "end", "Teacher"), t("T-2", 'Say "hi"; <i>', "end", 'a "q" <b>x</b>', "R;R"),
                        t("T-3", "Next", "semi;colon #h", "start", "Teacher")]})


@pytest.mark.parametrize("fmt", ["mermaid", "plantuml", "dot"])
def test_hostile_names_cannot_inject_markup(fmt):
    wf = hostile()
    outputs = [render_view("state", fmt, wf), render_view("journey", fmt, wf)]
    if fmt != "dot":
        outputs.append(render_view("sequence", fmt, wf, None, 'Say "hi"; <i>'))
    if fmt != "dot":  # DOT labels are always quoted strings, never HTML-like labels
        for text in outputs:
            assert "<b>" not in text and "<i>" not in text and "</b>" not in text
    if fmt == "mermaid":
        assert 'state "a #quot;q#quot; #lt;b#gt;x#lt;/b#gt;" as n_a__q___b_x__b_' in outputs[0]
        assert "state end" not in outputs[0] and "--> end\n" not in outputs[0]  # reserved word never used as an id
    if fmt == "plantuml":
        assert "<U+003C>b>x<U+003C>/b>" in outputs[0]
    if fmt == "dot":
        assert '"a \\"q\\" <b>x</b>"' in outputs[0]  # quoted and escaped, not an HTML-like label


def test_safe_ids_are_stable_unique_and_order_free():
    names = ["a b", "a_b", "a-b", "end", "Draft"]
    ids = safe_ids(names)
    assert len(set(ids.values())) == len(names) and ids["Draft"] == "Draft" and ids["end"] == "n_end"
    assert safe_ids(list(reversed(names))) == ids


def test_unsupported_and_unknown_requests_are_rejected():
    with pytest.raises(DomainError) as e:
        render_view("sequence", "dot", BEFORE, AFTER, "Recommend")
    assert e.value.code == "FORMAT_UNSUPPORTED"
    with pytest.raises(DomainError) as e:
        render_view("class", "svg", BEFORE)
    assert e.value.code == "FORMAT_UNSUPPORTED"
    for view, code in (("diff", "CANDIDATE_REQUIRED"), ("impact", "CANDIDATE_REQUIRED"), ("sequence", "ACTION_REQUIRED"), ("ripple", "VIEW_UNKNOWN")):
        with pytest.raises(DomainError) as e:
            render_view(view, "mermaid", BEFORE)
        assert e.value.code == code


def test_case_diagrams_payload_reports_sources_and_unsupported():
    full = case_diagrams(BEFORE, AFTER)
    assert full["sources"] == {"baseline": BEFORE.semantic_hash, "candidate": AFTER.semantic_hash}
    assert set(full["views"]["sequences"]) == {t.action for t in AFTER.transitions} and full["unsupported"] == []
    assert full["impact"]["complete"] and "Recommend" in full["impact"]["changed_actions"]
    no_candidate = case_diagrams(baseline(), None)
    assert no_candidate["views"]["diff"] is None and no_candidate["summary"] is None and no_candidate["sources"]["candidate"] is None
    assert set(no_candidate["views"]["sequences"]) == {t.action for t in BEFORE.transitions}
    dot = case_diagrams(BEFORE, AFTER, "dot")
    assert dot["unsupported"] == ["class", "sequence"] and dot["views"]["class"] is None and dot["views"]["diff"].startswith("//")
