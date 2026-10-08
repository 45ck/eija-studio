"""Simulate (ADR-0152): seeded simulated users whose every step the kernel decides, reported where they went."""
from __future__ import annotations

from pathlib import Path

import pytest

from eija_studio.application.simulation import MemorySession, run_log, simulate
from eija_studio.application.runtime import execute, initialise
from eija_studio.domain.models import DomainError, ExecuteCommand
from eija_studio.domain.pack import load_pack

ROOT = Path(__file__).resolve().parents[1]
PACKS = ("excursion", "library-loan", "eija-review-slice")


def pack(name):
    return load_pack(ROOT / "packs" / name)


@pytest.mark.parametrize("name", PACKS)
def test_a_seed_replays_exactly_and_the_totals_add_up(name):
    p = pack(name)
    run = simulate(p, p.model, seed=11, steps=300)
    assert run == simulate(p, p.model, seed=11, steps=300)
    assert run != simulate(p, p.model, seed=12, steps=300)
    assert run["attempts"] + run["records"] == 300 and run["committed"] + run["refused"] == run["attempts"]
    assert sum(t["committed"] for t in run["transitions"].values()) == run["committed"]
    assert sum(sum(t["refused"].values()) for t in run["transitions"].values()) == run["refused"] == sum(run["codes"].values())
    assert sum(s["now"] for s in run["states"].values()) == run["records"]
    assert run["model"] == p.model.semantic_hash and len(run["trace"]) <= 60


def test_every_logged_step_is_the_kernels_answer():
    """Replay the trace against a fresh kernel session and require the same outcome at every step."""
    p = pack("excursion")
    run = simulate(p, p.model, seed=3, steps=60)
    session, ids = MemorySession(p), {}
    for entry in run["trace"]:
        if entry["outcome"] == "CREATED":
            ids[entry["record"]] = initialise(session, "simulation", p.model, pack=p)["id"]
            continue
        version = session.instances[ids[entry["record"]]]["version"]
        stale = entry["outcome"] == "REFUSED" and entry["code"] == "STALE_VERSION"
        command = ExecuteCommand(operation_id=f"sim-{entry['step']}", actor_id=entry["actor"], instance_id=ids[entry["record"]],
                                 action=entry["action"], expected_version=version - 1 if stale else version)
        try:
            result = execute(session, "simulation", p.model, command, pack=p)
        except DomainError as refused:
            assert (entry["outcome"], entry["code"]) == ("REFUSED", refused.code)
        else:
            assert (entry["outcome"], entry["to"]) == ("COMMITTED", result["instance"]["state"])


def test_committed_effects_are_written_through_the_packs_adapters():
    p = pack("library-loan")
    run = simulate(p, p.model, seed=5, steps=400)
    notified = sum(run["transitions"][t.id]["committed"] for t in p.model.transitions
                   if any(e.startswith("Notification:") for e in t.required_effects))
    assert sum(run["effects"]["outbox"].values()) == notified > 0


def test_findings_name_elements_the_ide_can_select():
    p = pack("library-loan")
    run = simulate(p, p.model, seed=7, steps=5)  # too few steps to reach every state
    ids = {"state:" + s for s in p.model.states} | {"transition:" + t.id for t in p.model.transitions}
    assert run["findings"] and all(f["element"] in ids for f in run["findings"])
    assert any(f["severity"] == "warning" for f in run["findings"])


def test_bad_requests_are_refused():
    p, other = pack("excursion"), pack("library-loan")
    for kwargs, code in (({"steps": 0}, "INVALID_STEPS"), ({"steps": 10_000}, "INVALID_STEPS")):
        with pytest.raises(DomainError) as refused:
            simulate(p, p.model, **kwargs)
        assert refused.value.code == code
    with pytest.raises(DomainError) as refused:
        simulate(p, other.model)
    assert refused.value.code == "WORKFLOW_PACK_MISMATCH"


def test_transition_order_in_the_document_does_not_change_a_run():
    p = pack("library-loan")
    shuffled = p.model.model_copy(update={"transitions": tuple(reversed(p.model.transitions)),
                                          "states": tuple(reversed(p.model.states))})
    assert shuffled.semantic_hash == p.model.semantic_hash
    for steps in (5, 300):  # a short run has never-succeeded findings, a long one ties among refusals
        assert simulate(p, shuffled, seed=4, steps=steps) == simulate(p, p.model, seed=4, steps=steps)


@pytest.mark.parametrize("name", PACKS)
def test_the_run_log_is_the_whole_simulated_run_step_by_step(name):
    """The run bar (ADR-0160) moves through this log: every step, the same steps Simulate counts, the same each time."""
    p = pack(name)
    log, report = run_log(p, p.model, seed=11, steps=300), simulate(p, p.model, seed=11, steps=300)
    assert log == run_log(p, p.model, seed=11, steps=300) and log["format"] == "eija.run.v1"
    assert [e["step"] for e in log["trace"]] == list(range(1, 301))
    assert log["trace"][:60] == report["trace"]
    assert sum(e["outcome"] == "COMMITTED" for e in log["trace"]) == report["committed"]
    assert sum(e["outcome"] == "REFUSED" for e in log["trace"]) == report["refused"]
    assert log["stops"] == [] and len(log["records"]) == report["records"]


def test_breakpoints_stop_where_the_element_is_reached_and_refusals_when_asked():
    p = pack("library-loan")
    state, transition = p.model.states[2], p.model.transitions[0]
    marks = ["state:" + state, "transition:" + transition.id]
    log = run_log(p, p.model, seed=3, steps=400, breakpoints=marks)
    expected = [e["step"] for e in log["trace"]
                if e.get("transition") == transition.id or (e["outcome"] != "REFUSED" and e.get("to") == state)]
    assert expected and [s["step"] for s in log["stops"]] == expected
    assert {s["reason"] for s in log["stops"]} == {"breakpoint"} and log["breakpoints"] == sorted(marks)
    refusals = run_log(p, p.model, seed=3, steps=400, break_on_refusal=True)["stops"]
    assert [s["step"] for s in refusals] == [e["step"] for e in log["trace"] if e["outcome"] == "REFUSED"]
    assert all(s["reason"] == "exception" and s["code"] for s in refusals)
    assert run_log(p, p.model, seed=3, steps=400, breakpoints=marks)["trace"] == log["trace"]  # stops never change the run


def test_a_breakpoint_must_be_an_element_of_the_model():
    p = pack("excursion")
    for marks, code in ((["state:Nowhere"], "UNKNOWN_BREAKPOINT"), (["transition:TR-NONE"], "UNKNOWN_BREAKPOINT"),
                        ([f"state:{s}-{i}" for s in p.model.states for i in range(20)], "TOO_MANY_BREAKPOINTS")):
        with pytest.raises(DomainError) as refused:
            run_log(p, p.model, breakpoints=marks)
        assert refused.value.code == code
