"""Actors that are not people (ADR-0210): AI agents, timers and external systems as typed roles, and the laws about
the kind of actor that keep a person in the loop.

Proof: the refund desk pack's kind laws hold over every run, its test cases pass, and Simulate reports what each kind
of actor tried. Negative oracles: giving the AI agent the approval breaks all three kind laws in the policy and in the
law proof; a run made only of agent and machine steps breaks the person-in-the-loop law; a role the pack does not
declare never counts as a person (fail closed); a kind law with no role of its kinds, or an unknown kind, is refused
when the pack loads. Identity: a pack that names no kinds keeps its digest.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from eija_studio.application.law_proof import prove_laws, with_laws
from eija_studio.application.scenario_run import run_scenarios
from eija_studio.application.sequences import check_sequences
from eija_studio.application.simulation import simulate
from eija_studio.domain.laws import OnlyKindHolds, PathRequiresKind, Step, evaluate_run, evaluate_table
from eija_studio.domain.pack import PackError, load_pack, parse_pack
from eija_studio.domain.policy import apply_structural_all, check_policy
from eija_studio.domain.scenarios import scenarios_for
from eija_studio.domain.transactions import parse_transaction
from eija_studio.interfaces.http import create_app
from kernel_support import harness_studio

ROOT = Path(__file__).resolve().parents[1]
DESK = load_pack(ROOT / "packs" / "refund-desk")
LOAN = load_pack(ROOT / "packs" / "library-loan")
OPS = load_pack(ROOT / "packs" / "ai-ops")
KIND_LAWS = {"only-people-approve", "only-people-resolve", "approved-by-people", "person-in-the-loop", "payout-confirmed-by-gateway"}
SESSION = "synthetic-actor-kinds-test"
HEADERS = {"Authorization": "Bearer " + SESSION, "Origin": "http://127.0.0.1:8765"}


def document(pack):
    return json.loads((ROOT / "packs" / pack.id / "pack.json").read_text(encoding="utf-8"))


def agent_approves():
    """The change an eager proposer might make: the AI agent approves refunds itself."""
    return apply_structural_all(DESK.model, [parse_transaction({"kind": "set_role", "transition": "TR-APPROVE", "role": "SupportAgent"})], DESK)


def test_roles_carry_their_kind_and_a_person_is_the_default():
    assert {r.id: r.kind for r in DESK.roles} == {"Customer": "human", "SupportAgent": "agent", "Supervisor": "human",
                                                   "SlaTimer": "timer", "PaymentGateway": "system"}
    assert {r.kind for r in LOAN.roles} == {"human"} and DESK.role_kind("Nobody") is None


def test_a_pack_that_names_no_kinds_keeps_its_digest():
    raw = document(LOAN)
    explicit = copy.deepcopy(raw)
    for role in explicit["roles"]:
        role["kind"] = "human"
    assert parse_pack(explicit).digest == parse_pack(raw).digest == LOAN.digest
    assert all("kind" not in r for r in LOAN.model_dump(mode="json")["roles"])


def test_kind_laws_are_bound_to_the_roles_of_their_kinds():
    laws = {law.id: law for law in DESK.laws}
    assert laws["only-people-approve"].roles == {"Customer", "Supervisor"}
    assert laws["payout-confirmed-by-gateway"].roles == {"PaymentGateway"}


def test_every_law_of_the_refund_desk_holds_over_every_run():
    report = prove_laws(DESK)
    assert report["status"] == "HOLDS" and report["search"]["status"] == "COMPLETE"
    assert {v["id"] for v in report["laws"] if v["status"] == "HOLDS"} >= KIND_LAWS


def test_the_refund_desk_test_cases_pass():
    report = run_scenarios(DESK, DESK.model, scenarios_for(DESK))
    assert report["status"] == "PASS" and report["failed"] == 0 and report["passed"] == 7


def test_giving_the_agent_the_approval_breaks_the_kind_laws():
    candidate = agent_approves()
    assert {"HUMAN_DECISION:ApproveRefund", "HUMAN_DECISION:Approved", "HUMAN_IN_THE_LOOP:Paid"} <= set(check_policy(candidate, DESK))
    report = prove_laws(DESK, candidate)
    broken = {v["id"] for v in report["laws"] if v["status"] == "BROKEN"}
    assert report["status"] == "REFUSED" and {"only-people-approve", "approved-by-people", "person-in-the-loop"} <= broken


def test_a_run_of_agents_and_machines_alone_breaks_the_person_in_the_loop():
    law = next(x for x in DESK.laws if isinstance(x, PathRequiresKind))
    actions = {t.action for t in DESK.model.transitions}
    machines = [Step("AssessRequest", "SupportAgent", "Requested", "Assessed"), Step("ProposeRefund", "SupportAgent", "Assessed", "AwaitingApproval"),
                Step("ApproveRefund", "SupportAgent", "AwaitingApproval", "Approved"), Step("ConfirmPayout", "PaymentGateway", "Approved", "Paid")]
    signed = [*machines[:2], Step("ApproveRefund", "Supervisor", "AwaitingApproval", "Approved"), machines[3]]
    assert [v.law for v in evaluate_run([law], "Requested", machines, actions)] == ["person-in-the-loop"]
    assert evaluate_run([law], "Requested", signed, actions) == []


def test_a_role_the_pack_does_not_declare_never_counts_as_a_person():
    law = next(x for x in DESK.laws if x.id == "only-people-approve")
    stranger = agent_approves().model_copy(update={"transitions": tuple(
        t.model_copy(update={"role": "Contractor"}) if t.id == "TR-APPROVE" else t for t in DESK.model.transitions)})
    assert [v.law for v in evaluate_table([law], stranger)] == ["only-people-approve"]
    unbound = OnlyKindHolds(id="unbound", kind="only_kind_holds", code="X", role_kinds=("human",), action="ApproveRefund")
    assert [v.law for v in evaluate_table([unbound], DESK.model)] == ["unbound"]  # bound to no role: nothing counts


def test_a_kind_law_with_no_role_of_its_kinds_is_refused():
    raw = document(LOAN)
    raw["laws"].append({"id": "agents-never", "kind": "only_kind_holds", "code": "X", "role_kinds": ["agent"], "action": "Return"})
    with pytest.raises(PackError) as refused:
        parse_pack(raw)
    assert "laws[agents-never]: no declared role is of kind agent" in refused.value.diagnostics


def test_an_unknown_kind_is_refused():
    raw = document(DESK)
    raw["roles"][1]["kind"] = "robot"
    with pytest.raises(PackError):
        parse_pack(raw)


def test_the_proof_tracks_whether_a_counting_step_has_happened():
    """With the agent's hand-off, WithSupervisor is reached by the timer (counts for a law about people or timers) and by the
    agent (does not count), so the search keeps those two configurations apart; the law still holds because a person
    approves every refund that is paid."""
    law = {"id": "people-or-timers", "kind": "path_requires_kind", "code": "HUMAN_IN_THE_LOOP:Paid", "role_kinds": ["timer", "human"],
           "state": "Paid"}
    draft = with_laws(DESK, [*document(DESK)["laws"], law])
    handoff = apply_structural_all(DESK.model, DESK.meaning("agent_hands_off").transactions, DESK)
    report = prove_laws(draft, handoff)
    assert next(v for v in report["laws"] if v["id"] == "people-or-timers")["status"] == "HOLDS"
    assert report["search"]["configurations"] == len(handoff.states) + 1


def test_simulate_reports_what_each_kind_of_actor_tried():
    result = simulate(DESK, DESK.model, seed=1, steps=500)
    kinds = result["by_kind"]
    assert list(kinds) == ["human", "agent", "timer", "system"]
    assert kinds["agent"]["roles"] == ["SupportAgent"] and kinds["agent"]["codes"]["ACTOR_REVOKED"] > 0  # the paused agent
    assert sum(k["attempts"] for k in kinds.values()) == result["attempts"]
    assert all(k["attempts"] == k["committed"] + k["refused"] for k in kinds.values())


def test_the_page_reads_each_roles_kind(tmp_path):
    app = create_app(harness_studio(tmp_path / "workspace", pack=DESK), SESSION)
    try:
        client = TestClient(app, base_url=HEADERS["Origin"])
        assert client.get("/api/play/roles").status_code == 401
        roles = client.get("/api/play/roles", headers=HEADERS).json()["roles"]
        assert {r["id"]: r["kind"] for r in roles}["SlaTimer"] == "timer"
    finally:
        app.state.play.stop()


def test_a_kind_path_law_on_the_initial_state_judges_steps_back_into_it():
    """A new record in the initial state took no step; a machine step back into it breaks the law, on the table as on
    the run, so the policy never allows a model whose runs break the law."""
    raw = document(DESK)
    raw["laws"].append({"id": "people-reopen", "kind": "path_requires_kind", "code": "HUMAN_IN_THE_LOOP:Requested",
                        "role_kinds": ["human"], "state": "Requested"})
    pack = parse_pack(raw)
    law = next(x for x in pack.laws if x.id == "people-reopen")
    assert evaluate_table([law], pack.model) == []
    reopened = apply_structural_all(pack.model, [parse_transaction(
        {"kind": "add_transition", "id": "TR-HANDOFF", "action": "HandOff", "from_state": "Assessed", "to_state": "Requested", "role": "SupportAgent"})], pack)
    run = [Step("AssessRequest", "SupportAgent", "Requested", "Assessed"), Step("HandOff", "SupportAgent", "Assessed", "Requested")]
    assert [v.law for v in evaluate_table([law], reopened)] == ["people-reopen"]
    assert [v.law for v in evaluate_run([law], "Requested", run, {"HandOff"})] == ["people-reopen"]


def test_the_ai_ops_pack_keeps_a_person_before_production():
    """A second agent-heavy pack: every law holds and its test cases pass; the agent signing its own deploy off, or
    reporting its own build green, breaks the kind laws."""
    assert prove_laws(OPS)["status"] == "HOLDS"
    assert run_scenarios(OPS, OPS.model, scenarios_for(OPS))["status"] == "PASS"
    for transition, role, code in (("TR-SIGNOFF", "OpsAgent", "HUMAN_IN_THE_LOOP:InProduction"), ("TR-GREEN", "OpsAgent", "PROTECTED_AUTHORITY:ReportGreen")):
        candidate = apply_structural_all(OPS.model, [parse_transaction({"kind": "set_role", "transition": transition, "role": role})], OPS)
        assert code in check_policy(candidate, OPS)


def test_sequence_lifelines_say_which_actors_are_not_people():
    report = check_sequences(DESK, DESK.model, scenarios_for(DESK))
    heads = {ll["name"]: ll for s in report["sequences"] for ll in s["lifelines"] if ll["kind"] == "actor"}
    assert heads["support-bot"]["actor_kind"] == "agent" and heads["support-bot"]["label"].startswith("«agent» ")
    assert heads["supervisor-on-shift"]["actor_kind"] == "human" and "«" not in heads["supervisor-on-shift"]["label"]
    refused = next(s for s in report["sequences"] if s["id"] == "agent-cannot-approve")
    assert refused["verdict"] == "PRODUCIBLE" and any(f["operator"] == "neg" for f in refused["fragments"])
