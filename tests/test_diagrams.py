"""Diagrams are generated projections of the executable model (ADR-0019, ADR-0023).

Golden files pin the text; the other tests are negative controls that would fail if a diagram were
hand-drawn, order-dependent, or disagreed with what the runtime actually does. Regenerate goldens with
`EIJA_UPDATE_GOLDEN=1 python -m pytest tests/test_diagrams.py` and review the diff.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import BaseModel

from eija_studio.application import diagram_emitters, diagrams
from eija_studio.application.diagram_catalog import VIEW_FORMATS, _summary_table, case_diagrams, demo_pair, docs_bundle, render_view
from eija_studio.application.diagram_emitters import emit, safe_ids
from eija_studio.application.diagrams import (
    Message, class_model, commit_sequence, mark_blocked, policy_violations, diff_graph, diff_summary, impact_graph,
)
from eija_studio.application.runtime import execute
from eija_studio.domain.impact import model_impact
from eija_studio.domain.models import DomainError, ExecuteCommand, Workflow
from eija_studio.domain.policy import baseline, check_policy

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_diagram_syntax import HOSTILE_ACTION, MARKER, hostile_candidate, hostile_workflow

GOLDEN = Path(__file__).parent / "golden"
EXT = {"mermaid": "mmd", "plantuml": "puml", "dot": "dot"}
BEFORE, AFTER = demo_pair()


def golden_cases():
    cases = []
    for fmt in EXT:
        cases += [(view, fmt, None) for view in ("state-baseline", "state-candidate", "diff", "impact", "journey", "class")
                  if fmt in VIEW_FORMATS[view.split("-")[0]]]
        if fmt in VIEW_FORMATS["sequence"]:
            cases += [("sequence-" + t.action.lower(), fmt, t.action) for t in AFTER.transitions]
    return cases


def generate(view: str, fmt: str, action: str | None, before=BEFORE, after=AFTER) -> str:
    if view == "state-baseline":
        return render_view("state", fmt, before)
    if view == "state-candidate":
        return render_view("state", fmt, before, after)
    return render_view(view.split("-", maxsplit=1)[0], fmt, before, after, action)


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
    assert diff_summary(BEFORE, BEFORE) == {"initial_state": None, "added_states": [], "removed_states": [], "added_actions": [], "removed_actions": [], "changed_actions": {}}


def _edit(wf: Workflow, **changes) -> Workflow:
    data = wf.model_dump(mode="json")
    data.update(changes)
    return Workflow.model_validate(data)


def _edit_transition(wf: Workflow, action: str, **changes) -> Workflow:
    data = wf.model_dump(mode="json")
    next(t for t in data["transitions"] if t["action"] == action).update(changes)
    return Workflow.model_validate(data)


def test_a_semantic_change_is_never_an_empty_diff():
    """Whenever semantic_hash differs, the diff graph, its legend and the summary must say so."""
    variants = {
        "initial_state": _edit(AFTER, initial_state="Submitted"),
        "transition id": _edit_transition(AFTER, "Recommend", id="T-RENAMED"),
        "guard": _edit_transition(AFTER, "Approve", guards=[*next(t for t in AFTER.transitions if t.action == "Approve").guards, "actor_assigned"]),
        "required effect": _edit_transition(AFTER, "Approve", required_effects=["Audit:ExcursionApproved", "Audit:Extra"]),
        "forbidden effect": _edit_transition(AFTER, "Approve", forbidden_effects=["PaymentCaptured", "Extra"]),
        "role": _edit_transition(AFTER, "Approve", role="Teacher"),
    }
    for name, mutated in variants.items():
        assert mutated.semantic_hash != AFTER.semantic_hash, name
        g, summary = diff_graph(AFTER, mutated), diff_summary(AFTER, mutated)
        assert any(n.status != "same" for n in g.nodes) or any(e.status != "same" for e in g.edges) or g.initial_removed, name
        assert g.legend, name
        assert summary["initial_state"] or summary["changed_actions"], name
        assert "classDef" in render_view("diff", "mermaid", AFTER, mutated), name


def test_initial_state_change_marks_the_start_marker_and_summary():
    moved = _edit(AFTER, initial_state="Submitted")
    g, summary = diff_graph(AFTER, moved), diff_summary(AFTER, moved)
    assert summary["initial_state"] == {"before": "Draft", "after": "Submitted"} and summary["changed_actions"] == {}
    assert {n.id: n.status for n in g.nodes}["Draft"] == "changed" and {n.id: n.status for n in g.nodes}["Submitted"] == "changed"
    mermaid = render_view("diff", "mermaid", AFTER, moved)
    assert "[*] --> Draft: - start" in mermaid and "[*] --> Submitted: + start" in mermaid
    assert "- start" in render_view("diff", "plantuml", AFTER, moved) and "- start" in render_view("diff", "dot", AFTER, moved)
    assert "initial state" in _summary_text(AFTER, moved)


def test_transition_id_rename_is_reported_with_before_and_after():
    renamed = _edit_transition(AFTER, "Recommend", id="T-RENAMED")
    old = next(t.id for t in AFTER.transitions if t.action == "Recommend")
    assert diff_summary(AFTER, renamed)["changed_actions"] == {"Recommend": [{"field": "id", "before": old, "after": "T-RENAMED"}]}
    assert f"id {old}→T-RENAMED" in render_view("diff", "mermaid", AFTER, renamed)


def test_a_changed_edge_says_what_changed():
    guards = next(t for t in AFTER.transitions if t.action == "Approve").guards
    cases = {
        "role Registrar→Teacher": _edit_transition(AFTER, "Approve", role="Teacher"),
        "guards +actor_assigned": _edit_transition(AFTER, "Approve", guards=[*guards, "actor_assigned"]),
        "required_effects +Audit:Extra": _edit_transition(AFTER, "Approve", required_effects=["Audit:ExcursionApproved", "Audit:Extra"]),
        "forbidden_effects +Extra": _edit_transition(AFTER, "Approve", forbidden_effects=["PaymentCaptured", "Extra"]),
    }
    for note, mutated in cases.items():
        labels = [e.label for e in diff_graph(AFTER, mutated).edges if e.status == "changed"]
        assert len(labels) == 1 and labels[0].startswith("~ Approve · ") and note in labels[0], (note, labels)
    unchanged = [e.label for e in diff_graph(AFTER, AFTER).edges]
    assert all(not label.startswith("~") for label in unchanged)


def _summary_text(before: Workflow, after: Workflow) -> str:
    return _summary_table(before, after)


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
    text = render_view("sequence", "mermaid", BEFORE, AFTER, "Recommend").replace("#58;", ":")  # colons are entity-escaped for Mermaid
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


@pytest.mark.parametrize("fmt", ["mermaid", "plantuml", "dot"])
def test_hostile_names_cannot_inject_markup(fmt):
    wf = hostile_workflow()
    outputs = [render_view("state", fmt, wf), render_view("journey", fmt, wf)]
    if fmt != "dot":
        outputs.append(render_view("sequence", fmt, wf, None, HOSTILE_ACTION))
        for text in outputs:  # DOT labels are always quoted strings, never HTML-like labels
            assert "<b>" not in text and "<i>" not in text and "</b>" not in text
    if fmt == "mermaid":
        assert 'state "a #quot;quoted#quot; #lt;b#gt;x#lt;/b#gt;" as n_a__quoted___b_x__b_' in outputs[0]
        assert "state end" not in outputs[0] and "--> end\n" not in outputs[0]  # reserved word never used as an id
    if fmt == "plantuml":
        assert "<U+003C>b>x<U+003C>/b>" in outputs[0]
        for text in outputs:  # PlantUML evaluates %getenv(), %load_json(), %file_exists(), %date() inside labels
            assert not re.search(r"%\w+\(", text)
        assert "<U+0025>getenv(PLANTUML_SECRETVAR)" in outputs[0]
        assert MARKER not in "".join(outputs)
    if fmt == "dot":
        assert '"a \\"quoted\\" <b>x</b>"' in outputs[0]  # quoted and escaped, not an HTML-like label


def test_plantuml_percent_escape_has_a_negative_control():
    """The escape is what removes `%name(`: a raw label would match the pattern the test above forbids."""
    assert re.search(r"%\w+\(", 'state "%getenv(X)" as a')
    assert not re.search(r"%\w+\(", diagram_emitters._puml("%getenv(X)")) and "%" not in diagram_emitters._puml("100%")


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


def one_sided_reorder(wf: Workflow) -> Workflow:
    """Reverse only the unordered fields inside each transition, plus the transition list."""
    data = wf.model_dump(mode="json")
    data["transitions"] = list(reversed(data["transitions"]))
    for t in data["transitions"]:
        for key in ("guards", "required_effects", "forbidden_effects"):
            t[key] = list(reversed(t[key]))
    return Workflow.model_validate(data)


@pytest.mark.parametrize("fmt", ["mermaid", "plantuml", "dot"])
def test_reordering_only_the_candidate_changes_nothing_in_any_view(fmt):
    """Reordering guards or effects is not a change: the ripple must agree with the diff and with the semantic hash
    (the kernel's `model_impact` once compared transitions as tuples; see tests/test_domain.py)."""
    twin = one_sided_reorder(AFTER)
    assert twin != AFTER and twin.semantic_hash == AFTER.semantic_hash
    assert model_impact(BEFORE, twin)["changed_actions"] == model_impact(BEFORE, AFTER)["changed_actions"]  # kernel: order is not a change
    for view in ("state", "diff", "impact", "journey"):
        if fmt in VIEW_FORMATS[view]:
            assert render_view(view, fmt, BEFORE, twin) == render_view(view, fmt, BEFORE, AFTER), view
    assert render_view("impact", "mermaid", twin, AFTER) == render_view("impact", "mermaid", AFTER, AFTER)
    assert case_diagrams(BEFORE, twin)["impact"] == case_diagrams(BEFORE, AFTER)["impact"]
    assert diff_summary(AFTER, twin)["changed_actions"] == {}


def test_an_id_only_change_is_drawn_and_summarised():
    data = AFTER.model_dump(mode="json")
    for t in data["transitions"]:
        if t["action"] == "Approve":
            t["id"] = "T-APPROVE-RENAMED"
    renamed = Workflow.model_validate(data)
    assert renamed.semantic_hash != AFTER.semantic_hash and model_impact(AFTER, renamed)["changed_actions"] == ["Approve"]
    assert diff_summary(AFTER, renamed)["changed_actions"]["Approve"][0]["field"] == "id"
    text = render_view("diff", "mermaid", AFTER, renamed)
    assert "~ Approve · Registrar" in text and "class Approved,Recommended changed" in text
    assert any(n.status == "changed" for n in impact_graph(AFTER, renamed).nodes)


def teacher_approves() -> Workflow:
    data = AFTER.model_dump(mode="json")
    for t in data["transitions"]:
        if t["action"] == "Approve":
            t["role"] = "Teacher"
    return Workflow.model_validate(data)


VIEW_CASES = [(v, f, a) for v, a in (("state", None), ("diff", None), ("impact", None), ("journey", None), ("sequence", "Approve"))
              for f in ("mermaid", "plantuml")]


@pytest.mark.parametrize("view,fmt,action", VIEW_CASES)
def test_a_policy_refused_workflow_is_drawn_as_blocked(view, fmt, action):
    bad = teacher_approves()
    assert check_policy(bad) == ["PROTECTED_AUTHORITY:Approve"] and check_policy(AFTER) == []
    text = render_view(view, fmt, BEFORE, bad, action)
    assert "POLICY BLOCKED: PROTECTED_AUTHORITY:Approve" in text
    assert "POLICY BLOCKED" not in render_view(view, fmt, BEFORE, AFTER, action)  # negative control: an accepted candidate has no marker
    if view != "sequence" and fmt == "mermaid":
        assert "blocked" in text  # the node carries the red `blocked` class, not just text


def test_the_blocked_marker_cannot_collide_with_a_state_name():
    data = AFTER.model_dump(mode="json")
    data["states"] = [*data["states"], "policy-blocked"]
    bad = Workflow.model_validate(data)
    ids = [n.id for n in mark_blocked(diff_graph(BEFORE, bad), policy_violations(bad)).nodes]
    assert len(ids) == len(set(ids)) and "policy-blocked_" in ids
    assert "POLICY BLOCKED: UNSUPPORTED_WORKFLOW_SHAPE" in render_view("state", "mermaid", BEFORE, bad)


class SpyUnitOfWork:
    """A recording unit of work: answers exactly what `execute` needs and logs the order of port calls."""

    def __init__(self, model: Workflow, state: str, actor: dict):
        self.calls: list[str] = []
        self.item = {"id": "i1", "case_id": "c1", "model_hash": model.semantic_hash, "state": state, "version": 0}
        self._actor = actor

    def find_instance(self, instance_id, case_id):
        self.calls.append("find_instance")
        return self.item

    def actor(self, actor_id):
        self.calls.append("actor")
        return self._actor

    def find_operation(self, operation_id):
        self.calls.append("find_operation")
        return None

    def update_instance(self, item, expected):
        self.calls.append("update_instance")

    def event(self, kind, body):
        self.calls.append("event")

    def enqueue(self, case_id, operation_id, effect, recipient):
        self.calls.append("enqueue")

    def record_operation(self, operation_id, binding, result):
        self.calls.append("record_operation")


# What each Store/Audit/Outbox message of the diagram stands for at the unit-of-work port. A message that is
# not listed fails the test, so a new step has to be mapped deliberately.
PORT_CALL = (("load instance", "find_instance"), ("load actor", "actor"), ("find operation", "find_operation"),
             ("compare-and-set", "update_instance"), ("append ", "event"), ("enqueue ", "enqueue"),
             ("record operation", "record_operation"))


def drawn_port_calls(workflow: Workflow, action: str) -> list[str]:
    """Port calls in the order the sequence diagram shows them (main path: not the failure fragments)."""
    calls = []
    for step in commit_sequence(workflow, action).steps:
        if isinstance(step, Message) and step.target in {"Store", "Audit", "Outbox"} and not step.text.startswith("commit "):
            matches = [call for prefix, call in PORT_CALL if step.text.startswith(prefix)]
            assert len(matches) == 1, f"unmapped diagram step {step.text!r}"
            calls.append(matches[0])
    return calls


@pytest.mark.parametrize("action", sorted(t.action for t in AFTER.transitions))
def test_sequence_matches_the_order_the_real_runtime_calls_its_port(action):
    """Conformance, not a same-author oracle: run the real `execute` against a recording unit of work and compare the
    order with the diagram. Moving the replay lookup before the authority check, or the audit write after the
    operation record, in runtime.py fails this test. (The diagram is still hand-encoded; this pins it to the runtime.)"""
    t = next(t for t in AFTER.transitions if t.action == action)
    spy = SpyUnitOfWork(AFTER, t.from_state, {"active": True, "role": t.role, "assigned": True})
    result = execute(spy, "c1", AFTER, ExecuteCommand(operation_id="op1", actor_id="a", instance_id="i1", action=action, expected_version=0))
    assert result["committed"]
    assert spy.calls == drawn_port_calls(AFTER, action), spy.calls
    assert spy.calls.index("actor") < spy.calls.index("find_operation")  # authority is checked BEFORE the replay lookup


def test_the_conformance_check_can_fail():
    """Negative control: a runtime that looked up the operation before the actor would not match the drawing."""
    t = next(t for t in AFTER.transitions if t.action == "Recommend")
    spy = SpyUnitOfWork(AFTER, t.from_state, {"active": True, "role": t.role, "assigned": True})
    execute(spy, "c1", AFTER, ExecuteCommand(operation_id="op1", actor_id="a", instance_id="i1", action="Recommend", expected_version=0))
    swapped = list(spy.calls)
    i, j = swapped.index("actor"), swapped.index("find_operation")
    swapped[i], swapped[j] = swapped[j], swapped[i]
    assert swapped != drawn_port_calls(AFTER, "Recommend")


def test_authority_guards_the_runtime_always_checks_are_always_drawn():
    """`check_actor` tests active and role with no guard lookup, so the diagram must not depend on the guards listed."""
    for action in ("Submit", "Approve", "Recommend"):
        text = render_view("sequence", "mermaid", BEFORE, AFTER, action)
        assert "ACTOR_REVOKED" in text and "ROLE_DENIED" in text
    assert "ASSIGNMENT_DENIED" not in render_view("sequence", "mermaid", BEFORE, AFTER, "Approve")  # conditional in the runtime too


def _puml_body(text: str) -> str:
    """Emitted PlantUML without comment lines, with the escaped percent removed: nothing else may contain `%`."""
    return chr(10).join(line for line in text.splitlines() if not line.startswith("'")).replace("<U+0025>", "")


def test_hostile_names_are_inert_in_every_emitted_text():
    """Mermaid breaks on a trailing colon, `:::` and a leading backtick; PlantUML expands `%name()` in labels (a
    `%load_json` state name inlines a local file). No emitter may pass them through raw, in any view, including
    the diff and ripple of a hostile candidate."""
    hostile, moved = hostile_workflow(), hostile_candidate()
    for fmt in EXT:
        for view in ("state", "journey", "diff", "impact"):
            text = render_view(view, fmt, hostile, moved)
            if fmt == "plantuml":
                assert "%" not in _puml_body(text), (view, text)
            if fmt == "mermaid":
                for line in text.splitlines():
                    assert not re.search(r":\s*$|:::|:\s*`|\|\"`", line), (view, line)
    assert "<U+0025>load_json" in render_view("state", "plantuml", hostile)
    for t in hostile.transitions:
        assert "%" not in _puml_body(render_view("sequence", "plantuml", hostile, None, t.action)), t.action
        assert not re.search(r":\s*$", render_view("sequence", "mermaid", hostile, None, t.action), re.M)
