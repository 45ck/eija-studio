"""Simulate (ADR-0152): seeded simulated users whose every step the kernel decides, reported where they went."""
from __future__ import annotations

from pathlib import Path

import pytest

from eija_studio.application.simulation import MemorySession, simulate
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
