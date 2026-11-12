"""Guards over record values (issue #93, ADR-0234).

A transition may carry UML guards such as `[amount <= 500]` over the record class's attributes. The kernel refuses the
transition with VALUE_GUARD_DENIED unless every guard holds, failing closed on a missing value. Transitions without
guards keep their exact bytes and hashes. A build refuses guards that do not fit the data model; the law proof, Simulate,
the generated app's oracle and the SCXML differential try every combination of values the guards can tell apart.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from eija_studio.application import runtime
from eija_studio.application.appgen import generate, value_cases
from eija_studio.application.diagrams import state_graph
from eija_studio.application.law_proof import prove_laws, with_laws
from eija_studio.application.memo import model_hash
from eija_studio.application.scxml import guard_condition, to_scxml
from eija_studio.application.simulation import MemorySession, simulate
from eija_studio.domain.data import load_data
from eija_studio.domain.models import DomainError, ExecuteCommand, ValueGuard, Workflow
from eija_studio.domain.pack import load_pack
from eija_studio.domain.value_guards import guard_problems, points, valuations
from eija_studio.interfaces.app_build import conformance
from eija_studio.interfaces.cli import main
from verification.scope import OutsideFormalScope, require_formal_scope

ROOT = Path(__file__).resolve().parents[1]
DESK = load_pack(ROOT / "packs" / "refund-desk")
DATA = load_data(ROOT / "packs" / "refund-desk", "refund-desk")
SMALL = {"attribute": "amount", "op": "le", "value": 500}


def guarded(model: Workflow, **conditions: list[dict]) -> Workflow:
    raw = model.model_dump(mode="json")
    for t in raw["transitions"]:
        if t["id"] in conditions:
            t["conditions"] = conditions[t["id"]]
    return Workflow.model_validate(raw)


def _session(model: Workflow, state: str, values: dict) -> MemorySession:
    session = MemorySession(DESK)
    session.create_instance({"id": "r", "case_id": "c", "model_hash": model_hash(model), "state": state, "version": 0})
    session.record_values["r"] = values
    return session


def _approve(model: Workflow, values: dict) -> dict:
    session = _session(model, "AwaitingApproval", values)
    command = ExecuteCommand(operation_id="op", actor_id="supervisor-on-shift", instance_id="r", action="ApproveRefund",
                             expected_version=0)
    return runtime.execute(session, "c", model, command, pack=DESK)  # type: ignore[arg-type]


def test_a_guard_is_typed_and_fails_closed():
    with pytest.raises(ValueError):
        ValueGuard(attribute="paid", op="lt", value=True)
    with pytest.raises(ValueError):
        ValueGuard(attribute="name", op="gt", value="M")  # ordering is for numbers and dates only
    with pytest.raises(ValueError):
        ValueGuard(attribute="amount", op="gt", value=float("nan"))
    late = ValueGuard(attribute="decidedOn", op="ge", value="2026-01-01")
    assert late.holds({"decidedOn": "2026-03-01"}) and not late.holds({"decidedOn": "2025-12-31"})
    small = ValueGuard(**SMALL)
    assert small.holds({"amount": 500}) and not small.holds({"amount": 500.5})
    assert not small.holds({}) and not small.holds({"amount": "400"}) and not small.holds({"amount": True})
    assert str(small) == "amount ≤ 500"
    with pytest.raises(ValueError):
        guarded(DESK.model, **{"TR-APPROVE": [SMALL, SMALL]})


def test_models_without_guards_keep_their_bytes_and_guards_are_a_set():
    for pack_dir in sorted(p for p in (ROOT / "packs").iterdir() if (p / "pack.json").is_file()):
        raw = json.loads((pack_dir / "pack.json").read_text(encoding="utf-8"))["model"]
        assert "conditions" not in json.dumps(Workflow.model_validate(raw).model_dump(mode="json")), pack_dir.name
    two = [SMALL, {"attribute": "reason", "op": "ne", "value": "Damaged"}]
    one, other = guarded(DESK.model, **{"TR-APPROVE": two}), guarded(DESK.model, **{"TR-APPROVE": two[::-1]})
    assert one.semantic_hash == other.semantic_hash != DESK.model.semantic_hash
    assert Workflow.model_validate(one.model_dump(mode="json")) == one


def test_the_kernel_refuses_unless_every_guard_holds():
    model = guarded(DESK.model, **{"TR-APPROVE": [SMALL]})
    assert _approve(model, {"amount": 400})["instance"]["state"] == "Approved"
    for values in ({"amount": 600}, {}):
        with pytest.raises(DomainError) as e:
            _approve(model, values)
        assert e.value.code == "VALUE_GUARD_DENIED"
        assert e.value.details == {"codes": ["VALUE_GUARD_DENIED"], "refs": ["transition:TR-APPROVE", "attribute:amount"]}
    assert _approve(DESK.model, {})["committed"]  # an unguarded transition never needs values


def test_an_unguarded_transition_never_reads_values():
    class NoValues(MemorySession):
        def values(self, instance_id):
            raise AssertionError("values read for an unguarded transition")

    session = NoValues(DESK)
    session.create_instance({"id": "r", "case_id": "c", "model_hash": model_hash(DESK.model), "state": "AwaitingApproval", "version": 0})
    command = ExecuteCommand(operation_id="op", actor_id="supervisor-on-shift", instance_id="r", action="ApproveRefund",
                             expected_version=0)
    assert runtime.execute(session, "c", DESK.model, command, pack=DESK)["committed"]  # type: ignore[arg-type]


def test_guards_are_checked_against_the_data_model():
    model = guarded(DESK.model, **{"TR-APPROVE": [SMALL]})
    assert guard_problems(model, DATA) == [] and guard_problems(DESK.model, None) == []
    assert guard_problems(model, None) == ["VALUE_GUARD_NO_DATA"]
    wrong = guarded(DESK.model, **{"TR-APPROVE": [{"attribute": "amount", "op": "eq", "value": "lots"},
                                                  {"attribute": "colour", "op": "eq", "value": "red"},
                                                  {"attribute": "reason", "op": "eq", "value": "NotAReason"}]})
    assert guard_problems(wrong, DATA) == ["VALUE_GUARD_UNKNOWN:colour", "VALUE_GUARD_TYPE:amount", "VALUE_GUARD_TYPE:reason"]
    with pytest.raises(DomainError) as e:
        generate(DESK, wrong, DATA)
    assert e.value.code == "VALUE_GUARD_INVALID"


def test_points_cover_every_region_the_guards_tell_apart():
    numbers = points([ValueGuard(attribute="a", op="gt", value=500), ValueGuard(attribute="a", op="le", value=100.5)])
    assert numbers == [None, 99.5, 100.5, 300.25, 500, 501]
    # Record numbers may be fractional: 5.5 lies between 5 and 6 and takes both guards.
    assert points([ValueGuard(attribute="a", op="gt", value=5), ValueGuard(attribute="a", op="lt", value=6)]) == [None, 4, 5, 5.5, 6, 7]
    edges = points([ValueGuard(attribute="d", op="ge", value="0001-01-01"), ValueGuard(attribute="d", op="le", value="9999-12-31")])
    assert edges == [None, "0001-01-01", "5000-07-02", "9999-12-31", "other"]  # no day outside the calendar
    dates = points([ValueGuard(attribute="d", op="lt", value="2026-01-01")])
    assert dates == [None, "2025-12-31", "2026-01-01", "2026-01-02", "other"]
    model = guarded(DESK.model, **{"TR-APPROVE": [SMALL], "TR-DECLINE": [{"attribute": "reason", "op": "eq", "value": "Damaged"}]})
    assert len(valuations(model)) == 4 * 3 and valuations(DESK.model) == [{}]


def test_too_many_combinations_refuse_the_build_rather_than_check_nothing():
    many = [{"attribute": name, "op": "gt", "value": 1} for name in ("amount", "a1", "a2", "a3", "a4", "a5")]
    model = guarded(DESK.model, **{"TR-APPROVE": many})
    with pytest.raises(DomainError) as e:
        value_cases(DESK, model)
    assert e.value.code == "VALUE_GUARD_TOO_MANY"


def test_the_law_proof_finds_values_that_strand_a_record():
    stuck = [{"attribute": "amount", "op": "le", "value": 500}]
    model = guarded(DESK.model, **{"TR-APPROVE": stuck, "TR-DECLINE": stuck, "TR-ESCALATE": stuck})
    ends = {"id": "every-refund-ends", "kind": "can_reach_end", "code": "STUCK", "states": ["Paid", "Declined", "Withdrawn"]}
    pack = with_laws(DESK, [law.model_dump(mode="json") for law in DESK.laws] + [ends])
    assert {v["id"]: v for v in prove_laws(pack)["laws"]}["every-refund-ends"]["status"] == "HOLDS"
    verdict = {v["id"]: v for v in prove_laws(pack, model)["laws"]}["every-refund-ends"]
    assert verdict["status"] == "BROKEN" and verdict["stuck"] == ["Assessed", "AwaitingApproval"]  # once proposed, it cannot end
    assert verdict["record_values"] == {}  # a record with no amount: guards fail closed, so it is stuck too
    assert prove_laws(pack, model)["search"]["status"] == "COMPLETE"


def test_simulated_records_get_values_and_meet_the_guard():
    model = guarded(DESK.model, **{"TR-APPROVE": [SMALL]})
    run = simulate(DESK, model, seed=2, steps=400)
    created = [e for e in run["trace"] if e["outcome"] == "CREATED"]
    assert created and all("values" in e for e in created)
    assert "VALUE_GUARD_DENIED" in json.dumps(run)
    plain = simulate(DESK, DESK.model, seed=2, steps=400)
    assert "values" not in json.dumps([e for e in plain["trace"] if e["outcome"] == "CREATED"])


def test_the_oracle_value_cases_and_the_scxml_projection():
    model = guarded(DESK.model, **{"TR-APPROVE": [SMALL]})
    cases = value_cases(DESK, model)
    assert {json.dumps(c["values"]): c["expect"]["outcome"] for c in cases} == {
        "{}": "REFUSED", '{"amount": 499}': "COMMITTED", '{"amount": 500}': "COMMITTED", '{"amount": 501}': "REFUSED"}
    assert value_cases(DESK, DESK.model) == []
    assert "_event.data.has_amount and _event.data.value_amount <= 500" in guard_condition(model.transition_for("ApproveRefund"))
    assert "has_amount" in to_scxml(DESK, model) and "has_amount" not in to_scxml(DESK, DESK.model)
    differential = pytest.importorskip("verification.scxml.differential")
    if differential.load is None:
        pytest.skip("python-statemachine is not installed")
    report = differential.compare(DESK, model)
    assert report["status"] == "PASS", report["disagreements"]


def test_the_state_diagram_writes_the_guard_and_the_formal_encodings_refuse_it():
    model = guarded(DESK.model, **{"TR-APPROVE": [SMALL]})
    assert any(e.label.startswith("ApproveRefund [amount ≤ 500]") for e in state_graph(model).edges)
    with pytest.raises(OutsideFormalScope):
        require_formal_scope(model)
    plain = Workflow.model_validate(DESK.model.model_dump(mode="json", exclude={"transitions": {"__all__": {"after"}}}))
    assert require_formal_scope(plain) is plain  # refund-desk's time event (ADR-0236) is outside the scope too


def _guarded_pack(tmp_path: Path) -> Path:
    pack_dir = tmp_path / "refund-desk"
    shutil.copytree(ROOT / "packs" / "refund-desk", pack_dir)
    doc = json.loads((pack_dir / "pack.json").read_text(encoding="utf-8"))
    for t in doc["model"]["transitions"]:
        if t["id"] == "TR-APPROVE":
            t["conditions"] = [SMALL]
    (pack_dir / "pack.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8", newline="\n")
    return pack_dir


def test_a_built_app_checks_values_and_conformance_catches_an_app_that_does_not(tmp_path):
    pack_dir, out = _guarded_pack(tmp_path), tmp_path / "app"
    assert main(["build", "--pack", str(pack_dir), "--out", str(out)]) == 0
    manifest = json.loads((out / "BUILD.json").read_text(encoding="utf-8"))
    assert manifest["conformance"]["status"] == "PASS", manifest["conformance"]
    assert json.loads((out / "tests" / "oracle.json").read_text(encoding="utf-8"))["value_cases"]
    service = out / "app" / "service.py"
    text = service.read_text(encoding="utf-8")
    marker = 'return json.loads(row["fields"]) if row else {}'
    assert marker in text
    service.write_text(text.replace(marker, 'return {"amount": 1}'), encoding="utf-8")  # negative control
    assert conformance(out)["status"] == "FAIL"
