"""One action may leave several states (ADR-0232, issue #148).

UML draws one `Cancel` arrow from several states. The kernel now allows it while every transition the action labels
is the same apart from its id and source state, so authority, laws, screens and use cases stay per action; the runtime
picks the transition leaving the record's state. The formal encodings still model one transition per action and
refuse anything else rather than encode only one of its transitions.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from eija_studio.application.appgen import generate
from eija_studio.application.ghost_diff import ghost_diff
from eija_studio.application.interop import FORMATS, detect_format, export_model, import_model
from eija_studio.application.law_proof import prove_laws
from eija_studio.application.new_system import parse_sketch
from eija_studio.application.runtime import execute, initialise
from eija_studio.application.simulation import CASE, MemorySession, simulate
from eija_studio.domain.data import data_for
from eija_studio.domain.impact import keyed, model_impact
from eija_studio.domain.models import DomainError, ExecuteCommand, Workflow
from eija_studio.domain.pack import load_pack
from eija_studio.domain.policy import apply_structural_all, check_policy
from eija_studio.domain.transactions import parse_transaction
from eija_studio.interfaces.cli import main
from verification.scope import OutsideFormalScope
from verification.tla.model import transition_table

ROOT = Path(__file__).resolve().parents[1]
LOAN = load_pack(ROOT / "packs" / "library-loan")


def with_return_late(model: Workflow = LOAN.model, **override: str) -> Workflow:
    """Library loan with `Return` also leaving Overdue, in place of the separate `ReturnLate` action."""
    data = model.model_dump(mode="json")
    ret = next(t for t in data["transitions"] if t["action"] == "Return")
    data["transitions"] = [t for t in data["transitions"] if t["action"] != "ReturnLate"]
    data["transitions"].append(ret | {"id": "TR-RETURN-OVERDUE", "from_state": "Overdue"} | override)
    return Workflow.model_validate(data)


def test_an_action_may_leave_several_states_but_only_alike():
    model = with_return_late()
    assert model.sources("Return") == ("OnLoan", "Overdue")
    assert model.transition_for("Return", "Overdue").id == "TR-RETURN-OVERDUE"
    assert model.transition_for("Return", "Requested").id == "TR-RETURN"  # not a source: any of them, for authority
    for odd in ({"from_state": "OnLoan"}, {"to_state": "Cancelled"}, {"role": "Clerk"}, {"required_effects": []}):
        with pytest.raises(ValueError):
            with_return_late(**odd)
    assert check_policy(model, LOAN) == []
    assert prove_laws(LOAN, model)["status"] == prove_laws(LOAN)["status"] == "HOLDS"


def _act(session, model, actor, record, action):
    item = session.instances[record]
    command = ExecuteCommand(operation_id=f"op-{record}-{actor}-{action}-{item['version']}", actor_id=actor, instance_id=record,
                             action=action, expected_version=item["version"])
    return execute(session, CASE, model, command, pack=LOAN)


def test_the_runtime_takes_the_transition_leaving_the_records_state():
    model, session = with_return_late(), MemorySession(LOAN)
    late = initialise(session, CASE, model, state="Overdue", pack=LOAN)["id"]
    assert _act(session, model, "librarian-assigned", late, "Return")["instance"]["state"] == "Returned"
    on_time = initialise(session, CASE, model, state="OnLoan", pack=LOAN)["id"]
    assert _act(session, model, "librarian-assigned", on_time, "Return")["instance"]["state"] == "Returned"
    fresh = initialise(session, CASE, model, state="Requested", pack=LOAN)["id"]
    with pytest.raises(DomainError) as wrong_state:
        _act(session, model, "librarian-assigned", fresh, "Return")
    assert wrong_state.value.code == "STATE_DENIED"
    with pytest.raises(DomainError) as wrong_role:  # authority is still checked before the state
        _act(session, model, "member-a", fresh, "Return")
    assert wrong_role.value.code != "STATE_DENIED"


def test_changing_what_an_action_shares_changes_every_transition_it_labels():
    model = with_return_late()
    tx = parse_transaction({"kind": "set_role", "transition": "TR-RETURN-OVERDUE", "role": "Clerk"})
    moved = apply_structural_all(model, [tx], LOAN)
    assert {t.role for t in moved.transitions if t.action == "Return"} == {"Clerk"}
    source = parse_transaction({"kind": "retarget_transition", "transition": "TR-RETURN-OVERDUE", "end": "source", "state": "Requested"})
    assert apply_structural_all(model, [source], LOAN).sources("Return") == ("OnLoan", "Requested")


def test_a_sketch_may_repeat_an_action_from_another_state_only_alike():
    sketch = "Requested -> OnLoan : CheckOut [Librarian]\nOnLoan -> Returned : Return [Librarian]\nOverdue -> Returned : Return [Librarian]"
    assert [t[0] for t in parse_sketch(sketch)["transitions"] if t[2] == "Return"] == ["OnLoan", "Overdue"]
    for bad in ("Overdue -> Requested : Return [Librarian]", "Overdue -> Returned : Return [Clerk]", "OnLoan -> Returned : Return [Librarian]"):
        with pytest.raises(Exception) as refused:
            parse_sketch(sketch.rsplit("\n", 1)[0] + "\n" + bad)
        assert "Return" in str(refused.value.args)


def test_diffs_keep_one_key_per_action_until_it_leaves_several_states():
    single, several = keyed(LOAN.model, LOAN.model)
    assert set(single) == {t.action for t in LOAN.model.transitions} == set(several)
    before, after = keyed(LOAN.model, with_return_late())
    assert "Return from Overdue" in set(after) - set(before) and "ReturnLate" in set(before) - set(after)
    assert model_impact(LOAN.model, with_return_late())["changed_actions"] == ["Return", "ReturnLate"]
    cases = [c for c in ghost_diff(LOAN.model, with_return_late())["use_cases"]["cases"] if c["action"] == "Return"]
    assert len(cases) == 1 and cases[0]["status"] == "same"  # gaining a source is still the same use case


def test_the_formal_encodings_refuse_rather_than_encode_one_of_its_transitions():
    assert transition_table(LOAN.model)
    with pytest.raises(OutsideFormalScope):
        transition_table(with_return_late())


def test_a_built_app_passes_conformance_and_the_oracle_lists_each_action_once(tmp_path):
    files, _ = generate(LOAN, with_return_late())
    actions = [c["action"] for c in json.loads(files["tests/oracle.json"])["cases"] if c["state"] == "Overdue" and c["actor"] == "clerk" and c["expected_version"] == 0]
    assert len(actions) == len(set(actions))
    pack_dir, out = tmp_path / "library-loan", tmp_path / "app"
    shutil.copytree(ROOT / "packs" / "library-loan", pack_dir)
    doc = json.loads((pack_dir / "pack.json").read_text(encoding="utf-8"))
    doc["model"] = with_return_late().model_dump(mode="json")
    (pack_dir / "pack.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8", newline="\n")
    screens = json.loads((pack_dir / "screens.json").read_text(encoding="utf-8"))
    screens["screens"] = [s for s in screens["screens"] if s.get("use_case") != "ReturnLate"]  # the action is gone
    (pack_dir / "screens.json").write_text(json.dumps(screens, indent=2) + "\n", encoding="utf-8", newline="\n")
    assert main(["build", "--pack", str(pack_dir), "--out", str(out)]) == 0
    assert json.loads((out / "BUILD.json").read_text(encoding="utf-8"))["conformance"]["status"] == "PASS"


def test_a_simulated_crowd_returns_overdue_loans_by_the_same_action():
    run = simulate(LOAN, with_return_late(), seed=5, steps=300)
    taken = {(e["action"], e["from"]) for e in run["trace"] if e["outcome"] == "COMMITTED"}
    assert ("Return", "Overdue") in taken or ("Return", "OnLoan") in taken


@pytest.mark.parametrize("fmt", FORMATS)
def test_a_uml_file_with_one_action_from_several_states_imports_as_typed_edits(fmt):
    data, model, suffix = data_for(LOAN), with_return_late(), {"xmi": ".xmi", "plantuml": ".puml", "mermaid": ".md", "drawio": ".drawio"}[fmt]
    text, _ = export_model(fmt, LOAN, model, data)
    same = import_model(detect_format("x" + suffix, text), text, LOAN, model, data)
    assert same["status"] == "CLEAN" and same["state_machine"]["transactions"] == [], same["unmapped"]
    onto = import_model(detect_format("x" + suffix, text), text, LOAN, None, data)["state_machine"]
    shape = lambda m: {(t.action, t.from_state, t.to_state, t.role) for t in m.transitions}  # noqa: E731
    assert shape(Workflow.model_validate(onto["candidate"])) == shape(model)


def test_an_arrow_that_contradicts_its_actions_first_arrow_is_reported_not_read():
    text, _ = export_model("plantuml", LOAN, with_return_late(), data_for(LOAN))
    odd = text.replace("Overdue --> Returned : Return", "Overdue --> Cancelled : Return")
    assert odd != text
    found = import_model("plantuml", odd, LOAN, with_return_late(), data_for(LOAN))
    assert found["status"] != "CLEAN" and any("Overdue -> Cancelled" in u["element"] for u in found["unmapped"])


def test_a_role_change_is_kept_when_an_action_also_gains_a_source():
    # Return gains a source that sorts before its old one (Cancelled < OnLoan) and changes role in the same change.
    after = with_return_late(from_state="Cancelled").model_dump(mode="json")
    after["transitions"] = [t | {"role": "Clerk"} if t["action"] == "Return" else t for t in after["transitions"]]
    case = next(c for c in ghost_diff(LOAN.model, Workflow.model_validate(after))["use_cases"]["cases"] if c["action"] == "Return")
    assert case["status"] == "changed" and case["was_role"] == "Librarian" and case["role"] == "Clerk"
