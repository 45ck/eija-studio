"""Opt-in live plan mode (ADR-0230): a model reads the request, the pack's meaning supplies the steps, the kernel checks.

Every provider here is a stub; nothing is sent anywhere. A live call is never the default: it needs a networked
provider, --allow-network at startup, and consent on that one request.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from eija_studio.adapters.live_plan_proposals import LivePlanProposer
from eija_studio.adapters.plan_proposals import OfflinePlanProposer
from eija_studio.application.plan import propose_plan
from eija_studio.application.ports import ProviderResult
from eija_studio.domain.models import Alternative, DomainError, Proposal
from eija_studio.domain.pack import load_pack
from eija_studio.interfaces.http import create_app
from kernel_support import harness_studio

ROOT = Path(__file__).resolve().parents[1]
SESSION = "synthetic-live-plan-test"
HEADERS = {"Authorization": "Bearer " + SESSION, "Origin": "http://127.0.0.1:8765"}


class Stub:
    """A provider that answers every request with one fixed meaning, and counts its calls."""
    name, networked = "stub", True

    def __init__(self, meaning: str):
        self.meaning, self.calls = meaning, 0

    def propose(self, request, model):
        self.calls += 1
        proposal = Proposal(summary="s", alternatives=(Alternative(interpretation=self.meaning, explanation="read by the stub"),), unknowns=())
        return ProviderResult(proposal, self.name, "stub-model", {}, True)

    def doctor(self):
        return {"provider": self.name, "ready": True}


def live(meaning: str) -> tuple[LivePlanProposer, Stub]:
    stub = Stub(meaning)
    return LivePlanProposer(stub, OfflinePlanProposer()), stub


def test_a_paraphrase_the_offline_rules_miss_is_planned_from_the_meaning_the_model_read():
    pack = load_pack(ROOT / "packs" / "refund-desk")
    proposer, stub = live("agent_hands_off")
    result = propose_plan("When the bot isn't confident about a refund, a supervisor should take over.", pack.model, pack, proposer)
    assert stub.calls == 1 and result["meaning"] == "agent_hands_off" and result["live"] is True
    assert result["preview"]["legal"] and result["provider"] == "live:stub"


def test_an_unsafe_reading_is_planned_as_asked_and_refused_by_the_kernel():
    pack = load_pack(ROOT / "packs" / "refund-desk")
    proposer, _ = live("agent_auto_approve")
    result = propose_plan("Let the support agent approve refunds itself.", pack.model, pack, proposer)
    assert result["meaning"] == "agent_auto_approve" and not result["preview"]["legal"]


def test_a_reading_with_nothing_to_plan_is_refused_in_words():
    pack = load_pack(ROOT / "packs" / "refund-desk")
    proposer, _ = live("unsupported")
    with pytest.raises(DomainError) as e:
        propose_plan("Paint the dashboard purple.", pack.model, pack, proposer)
    assert e.value.code == "PLAN_REQUEST_UNSUPPORTED" and "read by the stub" in e.value.message


def test_exact_phrases_stay_offline_and_never_reach_the_provider():
    pack = load_pack(ROOT / "packs" / "refund-desk")
    proposer, stub = live("agent_hands_off")
    state = pack.model.states[-1]
    result = propose_plan(f"add state Archived after {state}", pack.model, pack, proposer)
    assert stub.calls == 0 and result["meaning"] is None and len(result["steps"]) == 1
    # Provenance follows who answered: the phrase reader, not the model (Codex review on PR #219).
    assert result["live"] is False and result["provider"] == OfflinePlanProposer().name
    asked = propose_plan("Please let an agent hand this off to a human.", pack.model, pack, proposer)
    assert stub.calls == 1 and asked["live"] is True and asked["provider"] == proposer.name


def test_a_request_that_is_partly_exact_phrases_is_refused_before_anything_is_sent():
    """Fagan inspection 2026-11-13: the model plans one meaning, so the exact clause was dropped from the plan unseen."""
    pack = load_pack(ROOT / "packs" / "refund-desk")
    proposer, stub = live("agent_hands_off")
    state = pack.model.states[-1]
    with pytest.raises(DomainError) as e:
        propose_plan(f"add state Archived after {state} then let a supervisor take over when the bot is unsure", pack.model, pack, proposer)
    assert e.value.code == "PLAN_REQUEST_MIXED" and stub.calls == 0


def test_a_second_live_request_while_one_runs_is_refused_and_never_sent():
    """Fagan inspection 2026-11-13: the chat's live path had no single-flight guard, unlike every other provider call."""
    pack = load_pack(ROOT / "packs" / "refund-desk")
    proposer, stub = live("agent_hands_off")
    inner: list[str] = []
    first = stub.propose

    def reentrant(request, model):
        if stub.calls == 0:
            with pytest.raises(DomainError) as e:
                propose_plan("Please let an agent hand this off to a human.", pack.model, pack, proposer)
            inner.append(e.value.code)
        return first(request, model)

    stub.propose = reentrant
    result = propose_plan("Please let an agent hand this off to a human.", pack.model, pack, proposer)
    assert inner == ["PROVIDER_BUSY"] and stub.calls == 1 and result["live"] is True
    assert propose_plan("Please let an agent hand this off to a human.", pack.model, pack, proposer)["live"] is True  # released


def test_an_exact_phrase_naming_what_the_model_lacks_gets_the_phrase_readers_answer_and_is_not_sent():
    """Fagan inspection 2026-11-13 (D5): the typo went to the model, which planned an unrelated meaning instead."""
    pack = load_pack(ROOT / "packs" / "refund-desk")
    proposer, stub = live("agent_hands_off")
    with pytest.raises(DomainError) as e:
        propose_plan("add state Archived after Nowhere", pack.model, pack, proposer)
    assert e.value.code == "PLAN_UNKNOWN_NAME" and "Nowhere" in e.value.message and stub.calls == 0


def test_every_live_call_is_audited_by_a_hash_never_the_request():
    """Fagan inspection 2026-11-13 (D6): live chat calls left no audit event, unlike Studio.propose."""
    pack = load_pack(ROOT / "packs" / "refund-desk")
    proposer, _ = live("agent_hands_off")
    events: list[tuple[str, dict]] = []
    proposer.audit = lambda kind, body: events.append((kind, body))
    request = "Please let an agent hand this off to a human."
    propose_plan(request, pack.model, pack, proposer)
    assert [k for k, _ in events] == ["PlanProviderCallStarted", "PlanProposalReceived"]
    assert events[0][1]["request_hash"] and request not in repr(events) and events[1][1]["meaning"] == "agent_hands_off"
    failing, _ = live("agent_hands_off")
    failing.audit = lambda kind, body: events.append((kind, body))

    def refuse(request, model):
        raise DomainError("PROVIDER_TRANSPORT", "timed out")

    failing.provider.propose = refuse
    with pytest.raises(DomainError):
        propose_plan(request, pack.model, pack, failing)
    assert events[-1][0] == "PlanProviderCallNotAccepted" and events[-1][1]["error_code"] == "PROVIDER_TRANSPORT"


def test_bootstrap_wires_the_live_proposer_to_the_studio_audit_log(tmp_path):
    from eija_studio.bootstrap import build_studio  # noqa: PLC0415

    studio = build_studio(tmp_path / "w", provider="openai", model="some-model", key="sk-test-not-used")
    assert studio.live_plan_proposer is not None and studio.live_plan_proposer.audit == studio.record
    studio.record("PlanProviderCallStarted", {"attempt_id": "a", "provider": "openai", "request_hash": "h", "egress": True})


@pytest.fixture
def client_for(tmp_path):
    def make(*, live_proposer, allow_network):
        studio = harness_studio(tmp_path / "workspace")
        studio.live_plan_proposer, studio.allow_network = live_proposer, allow_network
        return TestClient(create_app(studio, SESSION), base_url=HEADERS["Origin"])
    return make


def _plan(client, consent):
    model = client.get("/api/status", headers=HEADERS).json()["baseline"]
    return client.post("/api/play/plan", json={"model": model, "request": "Let teachers sign off excursions.", "consent": consent}, headers=HEADERS)


def test_without_a_live_provider_the_status_hides_live_ai_and_consent_is_refused(client_for):
    client = client_for(live_proposer=None, allow_network=False)
    assert client.get("/api/status", headers=HEADERS).json()["live_plan"] is False
    assert _plan(client, consent=False).status_code == 200
    refused = _plan(client, consent=True)
    assert refused.status_code >= 400 and refused.json()["code"] == "EGRESS_CONSENT_REQUIRED"


def test_network_off_at_startup_refuses_consent_even_with_a_live_provider(client_for):
    proposer, stub = live("recommend_only")
    client = client_for(live_proposer=proposer, allow_network=False)
    assert client.get("/api/status", headers=HEADERS).json()["live_plan"] is False
    assert _plan(client, consent=True).json()["code"] == "EGRESS_CONSENT_REQUIRED" and stub.calls == 0


def test_the_live_provider_is_used_only_for_a_request_with_consent(client_for):
    proposer, stub = live("recommend_only")
    client = client_for(live_proposer=proposer, allow_network=True)
    assert client.get("/api/status", headers=HEADERS).json()["live_plan"] is True
    offline = _plan(client, consent=False).json()
    assert stub.calls == 0 and offline["live"] is False
    asked = _plan(client, consent=True).json()
    assert stub.calls == 1 and asked["live"] is True and asked["meaning"] == "recommend_only"


def test_consent_must_be_a_real_boolean(client_for):
    proposer, stub = live("recommend_only")
    client = client_for(live_proposer=proposer, allow_network=True)
    assert _plan(client, consent="yes").status_code == 422 and stub.calls == 0


@pytest.mark.browser
@pytest.mark.slow
@pytest.mark.skipif(__import__("os").environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1")
def test_an_offline_studio_shows_no_live_ai_box_in_the_chat():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it
    from test_play_place import _launch  # noqa: PLC0415

    with ephemeral_eija_server(pack=ROOT / "packs" / "library-loan") as server, api.sync_playwright() as playwright:
        chrome = _launch(api, playwright)
        try:
            page = chrome.new_page(viewport={"width": 1280, "height": 800})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            assert page.is_hidden("#chat-live-row")
            page.fill("#chat-input", "Let librarians renew overdue loans.")
            page.click("#chat-send")
            page.wait_for_selector("#chat-log .msg.ai >> nth=1", timeout=30_000)
            assert not errors, errors
        finally:
            chrome.close()


# --- plan_check: the MCP dry run a coding agent calls before writing code --------------------------------------
def _surface(tmp_path, pack_id):
    from eija_studio.interfaces.mcp_server import AgentSurface, StudioAgentPort  # noqa: PLC0415 - needs the agents extra
    return AgentSurface(StudioAgentPort(harness_studio(tmp_path / "w", pack=ROOT / "packs" / pack_id)))


def test_plan_check_accepts_a_legal_plan_and_names_the_law_an_unsafe_one_breaks(tmp_path):
    pytest.importorskip("mcp", reason="NOT_RUN: install the agents extra")
    pack = load_pack(ROOT / "packs" / "refund-desk")
    surface = _surface(tmp_path, "refund-desk")
    safe = [t.model_dump(mode="json") for t in pack.meaning("agent_hands_off").transactions]
    unsafe = [t.model_dump(mode="json") for t in pack.meaning("agent_auto_approve").transactions]
    ok = surface.plan_check(safe)
    assert ok["legal"] is True and ok["applied"] is False and ok["persisted"] is False
    refused = surface.plan_check(unsafe)
    assert refused["legal"] is False and "law:only-people-approve" in refused["refs"]


def test_plan_check_stores_nothing_and_rejects_an_empty_plan(tmp_path):
    pytest.importorskip("mcp", reason="NOT_RUN: install the agents extra")
    surface = _surface(tmp_path, "refund-desk")
    before = surface.list_cases()
    with pytest.raises(DomainError) as e:
        surface.plan_check([])
    assert e.value.code == "INVALID_PLAN" and surface.list_cases() == before


def test_plan_check_on_a_system_you_started_declares_new_names_as_the_chat_does(tmp_path):
    """Fagan inspection 2026-11-13 (D7): plan_check always checked as a shipped pack and refused new vocabulary."""
    pytest.importorskip("mcp", reason="NOT_RUN: install the agents extra")
    from eija_studio.interfaces.mcp_server import AgentSurface, StudioAgentPort  # noqa: PLC0415

    studio = harness_studio(tmp_path / "w", pack=ROOT / "packs" / "refund-desk")
    state = studio.pack.model.states[0]
    steps = [{"kind": "add_state", "state": "Archived", "after": None},
             {"kind": "add_transition", "id": "TR-ARCHIVE", "action": "Archive", "from_state": state, "to_state": "Archived",
              "role": studio.pack.roles[0].id}]
    shipped = AgentSurface(StudioAgentPort(studio)).plan_check(steps)
    assert shipped["legal"] is False and shipped["grows"] is False
    studio.grows = True
    started = AgentSurface(StudioAgentPort(studio)).plan_check(steps)
    assert started["legal"] is True and started["grows"] is True and started["declared"] == {"actions": ["Archive"], "roles": []}


def test_eija_mcp_checks_as_a_started_system_only_for_a_pack_in_the_systems_home(tmp_path):
    from argparse import Namespace  # noqa: PLC0415
    from eija_studio.interfaces.cli import _started_in_playide  # noqa: PLC0415

    home = tmp_path / "home"
    (home / "coffee").mkdir(parents=True)
    (home / "coffee" / "pack.json").write_text("{}", encoding="utf-8")
    assert _started_in_playide(Namespace(pack=home / "coffee", systems=home)) is True
    assert _started_in_playide(Namespace(pack=ROOT / "packs" / "refund-desk", systems=home)) is False
    assert _started_in_playide(Namespace(pack=None, systems=home)) is False


def test_a_limit_on_a_value_or_a_time_is_refused_before_anything_is_sent():
    """Inspection 2026-11-14 P1: a limit no plan step can hold went to the model, which planned the step without it."""
    pack = load_pack(ROOT / "packs" / "refund-desk")
    proposer, stub = live("agent_hands_off")
    with pytest.raises(DomainError) as e:
        propose_plan("Let an agent hand off refunds over 500 to a human.", pack.model, pack, proposer)
    assert e.value.code == "PLAN_LIMIT_UNSUPPORTED" and stub.calls == 0
