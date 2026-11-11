"""Separation of duties (issue #149, ADR-0233).

A `distinct_actors` law says no single actor takes two of its actions on one record, such as assessing a refund and
then proposing it, or proposing it and then approving it after a change of role. The kernel refuses the second step
with SEPARATION_DENIED and names the law; the same action repeated is allowed; the law proof asks the kernel; the
generated app's oracle checks the app refuses where the kernel does. No shipped pack carries the law, so every
existing model, digest and oracle keeps its bytes.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from eija_studio.application import runtime
from eija_studio.application.appgen import generate, separation_cases
from eija_studio.application.law_proof import prove_laws, with_laws
from eija_studio.application.memo import model_hash
from eija_studio.application.simulation import MemorySession, simulate
from eija_studio.domain.laws import DistinctActors, Step, evaluate_run, evaluate_table
from eija_studio.domain.models import DomainError, ExecuteCommand
from eija_studio.domain.pack import load_pack
from eija_studio.domain.policy import check_policy
from eija_studio.interfaces.app_build import conformance
from eija_studio.interfaces.cli import main

ROOT = Path(__file__).resolve().parents[1]
DESK = load_pack(ROOT / "packs" / "refund-desk")
LAW = {"id": "assessor-does-not-propose", "kind": "distinct_actors", "code": "SAME_ASSESSOR",
       "actions": ["AssessRequest", "ProposeRefund"], "description": "Whoever assesses a request does not propose it."}
APPROVAL = {"id": "proposer-does-not-approve", "kind": "distinct_actors", "code": "SAME_PROPOSER",
            "actions": ["ProposeRefund", "ApproveRefund"]}


def _pack(*laws: dict):
    return with_laws(DESK, [law.model_dump(mode="json") for law in DESK.laws] + list(laws))


def _session(pack, state: str = "Requested") -> MemorySession:
    session = MemorySession(pack)
    session.create_instance({"id": "r", "case_id": "c", "model_hash": model_hash(pack.model), "state": state, "version": 0})
    return session


def _act(session: MemorySession, pack, actor: str, action: str, n: int) -> dict:
    command = ExecuteCommand(operation_id=f"op-{n}", actor_id=actor, instance_id="r", action=action,
                             expected_version=session.instances["r"]["version"])
    return runtime.execute(session, "c", pack.model, command, pack=pack)  # type: ignore[arg-type]


def test_the_law_is_validated_and_never_breaks_the_table():
    with pytest.raises(ValueError):
        DistinctActors(id="x", code="X", kind="distinct_actors", actions=("A",))
    with pytest.raises(ValueError):
        DistinctActors(id="x", code="X", kind="distinct_actors", actions=("A", "A"))
    with pytest.raises(DomainError) as e:
        _pack(LAW | {"actions": ["AssessRequest", "Ghost"]})
    assert e.value.code == "LAWS_INVALID"
    pack = _pack(LAW)
    assert all(v.law != LAW["id"] for v in evaluate_table(pack.laws, pack.model))
    assert check_policy(pack.model, pack) == check_policy(DESK.model, DESK)


def test_the_same_actor_is_refused_the_second_action_and_another_actor_is_not():
    pack = _pack(LAW)
    session = _session(pack)
    assert _act(session, pack, "support-bot", "AssessRequest", 1)["committed"]
    with pytest.raises(DomainError) as e:
        _act(session, pack, "support-bot", "ProposeRefund", 2)
    assert e.value.code == "SEPARATION_DENIED"
    assert e.value.details == {"codes": ["SAME_ASSESSOR"], "refs": [f"law:{LAW['id']}", "action:AssessRequest",
                                                                  "action:ProposeRefund"]}
    assert session.instances["r"]["state"] == "Assessed" and session.acts("r") == [("AssessRequest", "support-bot")]
    session.actors["support-bot-2"] = session.actors["support-bot"] | {"id": "support-bot-2"}
    assert _act(session, pack, "support-bot-2", "ProposeRefund", 3)["instance"]["state"] == "AwaitingApproval"


def test_a_change_of_role_does_not_make_a_different_actor():
    pack = _pack(APPROVAL)
    session = _session(pack, "Assessed")
    _act(session, pack, "support-bot", "ProposeRefund", 1)
    session.actors["support-bot"] = session.actors["support-bot"] | {"role": "Supervisor", "assigned": True}  # promoted mid-record
    with pytest.raises(DomainError) as e:
        _act(session, pack, "support-bot", "ApproveRefund", 2)
    assert e.value.code == "SEPARATION_DENIED"
    assert _act(session, pack, "supervisor-on-shift", "ApproveRefund", 3)["committed"]


def test_without_the_law_nothing_is_recorded_and_nothing_changes():
    session = _session(DESK)
    _act(session, DESK, "support-bot", "AssessRequest", 1)
    _act(session, DESK, "support-bot", "ProposeRefund", 2)
    assert session.acts("r") == []


def test_a_replay_is_still_a_replay_and_a_refusal_writes_nothing():
    pack = _pack(LAW)
    session = _session(pack)
    first = _act(session, pack, "support-bot", "AssessRequest", 1)
    command = ExecuteCommand(operation_id="op-1", actor_id="support-bot", instance_id="r", action="AssessRequest",
                             expected_version=0)
    again = runtime.execute(session, "c", pack.model, command, pack=pack)  # type: ignore[arg-type]
    assert again["duplicate"] and again["original_result"] == first
    assert session.acts("r") == [("AssessRequest", "support-bot")]


def test_a_run_is_judged_on_who_took_each_step():
    law = DistinctActors(id="sod", code="SOD", kind="distinct_actors", actions=("Propose", "Approve"))
    steps = [Step("Propose", "A", "S0", "S1", actor="ann"), Step("Approve", "B", "S1", "S2", actor="ann")]
    assert [v.refs for v in evaluate_run([law], "S0", steps, {"Propose", "Approve"})] == [("law:sod", "step:1")]
    steps[1] = Step("Approve", "B", "S1", "S2", actor="bob")
    assert evaluate_run([law], "S0", steps, {"Propose", "Approve"}) == []
    again = [Step("Propose", "A", "S0", "S1", actor="ann"), Step("Propose", "A", "S1", "S1", actor="ann")]
    assert evaluate_run([law], "S0", again, {"Propose"}) == []  # resubmitting is not a second duty
    assert evaluate_run([law], "S0", [Step("Propose", "A", "S0", "S1"), Step("Approve", "B", "S1", "S2")], set()) == []


def test_the_law_proof_asks_the_kernel():
    report = prove_laws(_pack(LAW, APPROVAL))
    verdicts = {v["id"]: v for v in report["laws"]}
    assert verdicts[LAW["id"]]["status"] == "HOLDS" and verdicts[LAW["id"]]["method"] == "kernel"
    assert verdicts[APPROVAL["id"]]["status"] == "HOLDS"
    apart = {"id": "far-apart", "kind": "distinct_actors", "code": "FAR", "actions": ["AssessRequest", "ApproveRefund"]}
    assert {v["id"]: v for v in prove_laws(_pack(apart))["laws"]}["far-apart"]["status"] == "VACUOUS"


def test_the_law_proof_catches_a_kernel_that_does_not_separate(monkeypatch):
    monkeypatch.setattr(runtime, "separations", lambda pack, model, action: [])
    verdict = {v["id"]: v for v in prove_laws(_pack(LAW))["laws"]}[LAW["id"]]
    assert verdict["status"] == "BROKEN"
    assert [s["action"] for s in verdict["counterexample"]] == ["AssessRequest", "ProposeRefund"]


def test_simulate_shows_the_refusal():
    pack = _pack(LAW)
    run = simulate(pack, pack.model, seed=5, steps=400)
    assert "SEPARATION_DENIED" in json.dumps(run)
    assert "SEPARATION_DENIED" not in json.dumps(simulate(DESK, DESK.model, seed=5, steps=400))


def test_the_oracle_has_separation_cases_only_with_the_law():
    assert separation_cases(DESK, DESK.model) == []
    files, _ = generate(DESK, DESK.model)
    assert "separation_cases" not in json.loads(files["tests/oracle.json"])
    cases = separation_cases(_pack(LAW), DESK.model)
    assert {(c["actor"], c["first"], c["then"]) for c in cases} == {("support-bot", "AssessRequest", "ProposeRefund")}
    assert all(c["expect"] == {"outcome": "REFUSED", "code": "SEPARATION_DENIED"} for c in cases)


def _separated_pack(tmp_path: Path) -> Path:
    pack_dir = tmp_path / "refund-desk"
    shutil.copytree(ROOT / "packs" / "refund-desk", pack_dir)
    doc = json.loads((pack_dir / "pack.json").read_text(encoding="utf-8"))
    doc["laws"].append(LAW)
    (pack_dir / "pack.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8", newline="\n")
    return pack_dir


def test_a_built_app_refuses_and_conformance_catches_an_app_that_does_not(tmp_path):
    pack_dir, out = _separated_pack(tmp_path), tmp_path / "app"
    assert main(["build", "--pack", str(pack_dir), "--out", str(out)]) == 0
    manifest = json.loads((out / "BUILD.json").read_text(encoding="utf-8"))
    assert manifest["conformance"]["status"] == "PASS", manifest["conformance"]
    service = out / "app" / "service.py"
    text = service.read_text(encoding="utf-8")
    marker = 'self.db.execute("INSERT INTO acts(record_id, action, actor_id) VALUES(?,?,?)", (instance_id, action, actor_id))'
    assert marker in text
    service.write_text(text.replace(marker, "return None"), encoding="utf-8")
    assert conformance(out)["status"] == "FAIL"  # negative control: an app that forgets who acted
