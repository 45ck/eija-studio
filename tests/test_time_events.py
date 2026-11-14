"""Time events on transitions (issue #93 item 2, ADR-0237).

A transition may carry UML's `after(2 days)`: it may be taken only once the record has been in its source state that
long. The kernel reads the time through the `UnitOfWork.elapsed` port and refuses with TIMER_NOT_DUE before then; an
unknown entry time is never due. Transitions without a time event keep their exact bytes and hashes. The law proof lets
time pass, Simulate has simulated time, the built app keeps an entry time per record and its conformance run checks
the time cases, and the SCXML chart carries the time event as a `cond` term the differential checks.
"""
from __future__ import annotations

import importlib
import json
import shutil
from pathlib import Path

import pytest

from eija_studio.application import runtime
from eija_studio.application.appgen import generate, timer_cases
from eija_studio.application.diagrams import state_graph
from eija_studio.application.law_proof import prove_laws, with_laws
from eija_studio.application.memo import model_hash
from eija_studio.application.ghost_diff import ghost_diff
from eija_studio.application.scenario_run import record_steps, run_scenarios
from eija_studio.application.scxml import guard_condition, to_scxml
from eija_studio.application.simulation import MemorySession, simulate
from eija_studio.domain.impact import changed_fields
from eija_studio.domain.models import Delay, DomainError, ExecuteCommand, Workflow
from eija_studio.domain.pack import load_pack
from eija_studio.domain.scenarios import ScenarioStep, scenarios_for
from eija_studio.interfaces.app_build import conformance
from eija_studio.interfaces.cli import main
from verification.scope import OutsideFormalScope, require_formal_scope

ROOT = Path(__file__).resolve().parents[1]
DESK = load_pack(ROOT / "packs" / "refund-desk")
TWO_DAYS = 2 * 86400


def timed(model: Workflow, **delays: dict | None) -> Workflow:
    raw = model.model_dump(mode="json")
    for t in raw["transitions"]:
        if t["id"] in delays:
            t.pop("after", None)
            if delays[t["id"]] is not None:
                t["after"] = delays[t["id"]]
    return Workflow.model_validate(raw)


UNTIMED = timed(DESK.model, **{"TR-ESCALATE": None})


def _escalate(model: Workflow, waited: float | None) -> dict:
    session = MemorySession(DESK)
    session.create_instance({"id": "r", "case_id": "c", "model_hash": model_hash(model), "state": "AwaitingApproval", "version": 0})
    if waited is None:
        session.entered.pop("r")
    else:
        session.wait(waited)
    command = ExecuteCommand(operation_id="op", actor_id="sla-clock", instance_id="r", action="EscalateStale",
                             expected_version=0)
    return runtime.execute(session, "c", model, command, pack=DESK)  # type: ignore[arg-type]


def test_a_delay_is_typed_and_unknown_time_is_never_due():
    two = Delay(amount=2, unit="days")
    assert two.seconds == TWO_DAYS and str(two) == "after(2 days)" and str(Delay(amount=1, unit="hours")) == "after(1 hour)"
    assert two.due(TWO_DAYS) and not two.due(TWO_DAYS - 1) and not two.due(None) and not two.due(float("nan"))
    for bad in ({"amount": 0, "unit": "days"}, {"amount": 2, "unit": "weeks"}, {"amount": 1.5, "unit": "days"},
                {"amount": "2", "unit": "days"}):
        with pytest.raises(ValueError):
            Delay.model_validate(bad)


def test_the_kernel_refuses_a_step_before_it_is_due():
    assert DESK.model.transition_for("EscalateStale").after == Delay(amount=2, unit="days")
    assert _escalate(DESK.model, TWO_DAYS)["instance"]["state"] == "WithSupervisor"
    for early in (0, TWO_DAYS - 1, None):
        with pytest.raises(DomainError) as e:
            _escalate(DESK.model, early)
        assert e.value.code == "TIMER_NOT_DUE"
        assert e.value.details["refs"] == ["transition:TR-ESCALATE", "state:AwaitingApproval"]
    assert _escalate(UNTIMED, 0)["committed"]  # without the time event, any time will do


def test_every_committed_step_restarts_the_clock():
    loop = timed(DESK.model, **{"TR-ESCALATE": {"amount": 1, "unit": "hours"}})
    session = MemorySession(DESK)
    session.create_instance({"id": "r", "case_id": "c", "model_hash": model_hash(loop), "state": "Requested", "version": 0})
    session.wait(10_000)
    assert session.elapsed("r") == 10_000
    assign = ExecuteCommand(operation_id="op1", actor_id="support-bot", instance_id="r", action="AssessRequest", expected_version=0)
    runtime.execute(session, "c", loop, assign, pack=DESK)  # type: ignore[arg-type]
    assert session.elapsed("r") == 0


def test_models_without_time_events_keep_their_bytes_and_the_clock_is_never_read():
    assert "after" not in json.dumps(UNTIMED.model_dump(mode="json")) and UNTIMED.longest_wait == 0
    assert DESK.model.longest_wait == TWO_DAYS
    other = timed(DESK.model, **{"TR-ESCALATE": {"amount": 48, "unit": "hours"}})
    assert other.semantic_hash != DESK.model.semantic_hash != UNTIMED.semantic_hash
    before, after = UNTIMED.transition_for("EscalateStale"), DESK.model.transition_for("EscalateStale")
    assert before is not None and after is not None and changed_fields(before, after) == ["after"]

    class NoClock(MemorySession):
        def elapsed(self, instance_id: str) -> float | None:
            raise AssertionError("the clock was read for a transition without a time event")

    session = NoClock(DESK)
    session.create_instance({"id": "r", "case_id": "c", "model_hash": model_hash(DESK.model), "state": "AwaitingApproval", "version": 0})
    command = ExecuteCommand(operation_id="op", actor_id="supervisor-on-shift", instance_id="r", action="ApproveRefund",
                             expected_version=0)
    assert runtime.execute(session, "c", DESK.model, command, pack=DESK)["committed"]  # type: ignore[arg-type]


def test_every_transition_one_action_labels_shares_its_time_event():
    raw = DESK.model.model_dump(mode="json")
    extra = dict(next(t for t in raw["transitions"] if t["id"] == "TR-ESCALATE"), id="TR-ESCALATE-2", from_state="Assessed")
    extra.pop("after")
    raw["transitions"].append(extra)
    with pytest.raises(ValueError, match="ambiguous"):
        Workflow.model_validate(raw)


def test_the_law_proof_lets_time_pass():
    ends = {"id": "every-refund-ends", "kind": "can_reach_end", "code": "STUCK", "states": ["Paid", "Declined", "Withdrawn"]}
    pack = with_laws(DESK, [law.model_dump(mode="json") for law in DESK.laws] + [ends])
    report = prove_laws(pack)
    assert report["search"]["status"] == "COMPLETE" and "EscalateStale" not in report["search"]["never_committed"]
    assert "WithSupervisor" in report["search"]["reached"]
    assert {v["id"]: v for v in report["laws"]}["every-refund-ends"]["status"] == "HOLDS"
    assert prove_laws(pack, UNTIMED)["search"]["reached"] == report["search"]["reached"]  # waiting only adds steps


def test_simulated_time_makes_the_time_event_fall_due():
    run = simulate(DESK, DESK.model, seed=4, steps=600)
    assert run["time"]["seconds_per_step"] == TWO_DAYS / 12
    assert run["transitions"]["TR-ESCALATE"]["committed"] > 0
    assert run["transitions"]["TR-ESCALATE"]["refused"].get("TIMER_NOT_DUE", 0) > 0
    plain = simulate(DESK, UNTIMED, seed=4, steps=600)
    assert "time" not in plain and "TIMER_NOT_DUE" not in json.dumps(plain)


def test_the_oracle_timer_cases_and_the_scxml_projection():
    cases = timer_cases(DESK, DESK.model)
    assert [(c["waited"], c["expect"]) for c in cases] == [
        (TWO_DAYS / 2, {"outcome": "REFUSED", "code": "TIMER_NOT_DUE"}),
        (TWO_DAYS, {"outcome": "COMMITTED", "state": "WithSupervisor",
                    "effects": ["Audit:RefundEscalated", "Notification:SupervisorPaged"]})]
    assert timer_cases(DESK, UNTIMED) == []
    files, _ = generate(DESK)
    oracle = json.loads(files["tests/oracle.json"])
    assert oracle["waited"] == TWO_DAYS and len(oracle["timer_cases"]) == 2
    assert "waited" not in json.loads(generate(DESK, UNTIMED)[0]["tests/oracle.json"])
    escalate = DESK.model.transition_for("EscalateStale")
    assert escalate is not None and f"_event.data.has_elapsed and _event.data.elapsed >= {TWO_DAYS}" in guard_condition(escalate)
    assert "has_elapsed" not in to_scxml(DESK, UNTIMED)
    differential = importlib.import_module("verification.scxml.differential")  # first-party: a broken import must fail, not skip
    if differential.load is None:
        pytest.skip("python-statemachine is not installed")
    assert differential.compare(DESK)["status"] == "PASS"
    broken = to_scxml(DESK).replace(f" and _event.data.has_elapsed and _event.data.elapsed &gt;= {TWO_DAYS}", "")
    assert broken != to_scxml(DESK)
    assert differential.compare(DESK, document=broken)["status"] == "FAIL"  # negative control: the chart forgot the time


def test_the_state_diagram_writes_the_time_event_and_the_formal_encodings_refuse_it():
    assert any(e.label.startswith("EscalateStale after(2 days) · SlaTimer") for e in state_graph(DESK.model).edges)
    with pytest.raises(OutsideFormalScope, match="time events"):
        require_formal_scope(DESK.model)
    assert require_formal_scope(UNTIMED) is UNTIMED


def test_a_built_app_keeps_time_and_conformance_catches_an_app_that_does_not(tmp_path):
    pack_dir, out = tmp_path / "refund-desk", tmp_path / "app"
    shutil.copytree(ROOT / "packs" / "refund-desk", pack_dir)
    assert main(["build", "--pack", str(pack_dir), "--out", str(out)]) == 0
    manifest = json.loads((out / "BUILD.json").read_text(encoding="utf-8"))
    assert manifest["conformance"]["status"] == "PASS", manifest["conformance"]
    service = out / "app" / "service.py"
    text = service.read_text(encoding="utf-8")
    marker = 'return None if row is None or row["entered_at"] is None else now() - row["entered_at"]'
    assert marker in text
    service.write_text(text.replace(marker, "return 10.0 ** 9"), encoding="utf-8")  # negative control: always due
    assert conformance(out)["status"] == "FAIL"


def test_a_scenario_waits_and_the_time_event_falls_due():
    report = run_scenarios(DESK, DESK.model, scenarios_for(DESK))
    timer = next(s for s in report["scenarios"] if s["id"] == "timer-escalates")
    assert timer["status"] == "PASS"
    assert [(s.get("wait"), s["actual"]) for s in timer["steps"] if s["action"] == "EscalateStale"] == [
        ("1 day", {"refused": "TIMER_NOT_DUE"}), ("1 day", {"state": "WithSupervisor"})]
    plain = ScenarioStep.model_validate({"actor": "a", "action": "Go", "then": {"state": "Done"}})
    assert "wait" not in plain.model_dump(mode="json")


def test_the_ghost_diff_writes_a_changed_time_event():
    """Review regression: a changed `after` reached the ghost diff with no text for it."""
    three = timed(DESK.model, **{"TR-ESCALATE": {"amount": 3, "unit": "days"}})
    texts = [c["text"] for c in ghost_diff(DESK.model, three)["changes"]]
    assert any("time event after(2 days) → after(3 days)" in t for t in texts), texts
    added = [c["text"] for c in ghost_diff(UNTIMED, DESK.model)["changes"]]
    assert any("time event none → after(2 days)" in t for t in added), added
    json.dumps(ghost_diff(DESK.model, three))


def test_re_recording_a_scenario_keeps_its_waits():
    """Review regression: re-recording a timed scenario dropped its waits, so the escalation never fell due."""
    day = Delay(amount=1, unit="days")
    steps = record_steps(DESK, DESK.model, "AwaitingApproval",
                         [("sla-clock", "EscalateStale", day), ("sla-clock", "EscalateStale", day)])
    assert [(s.get("wait"), s["then"]) for s in steps] == [
        ({"amount": 1, "unit": "days"}, {"refused": "TIMER_NOT_DUE"}),
        ({"amount": 1, "unit": "days"}, {"state": "WithSupervisor"})]
    assert "wait" not in record_steps(DESK, DESK.model, None, [("customer-a", "Withdraw")])[0]
