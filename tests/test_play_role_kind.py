"""Who holds a role, shown and changed in PlayIDE (ADR-0210, issue #156).

A role's kind (a person, an AI agent, a timer or an external system) is protected policy input: the kind laws count
roles by kind. So changing it is a step in the plan, like a drawn edit, and the policy judges the plan with the draft's
kinds; nothing is written. "Who may take it" names each role's kind. The browser test is marked `browser`: it runs
only with EIJA_BROWSER_TESTS=1 (NOT_RUN otherwise) and never downloads a browser.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from eija_studio.application.data_steps import parse_step
from eija_studio.application.plan import preview_plan
from eija_studio.domain.models import DomainError
from eija_studio.domain.pack import load_pack

ROOT = Path(__file__).resolve().parents[1]
DESK = load_pack(ROOT / "packs" / "refund-desk")
LOAN = load_pack(ROOT / "packs" / "library-loan")
STEPS = "document.querySelectorAll('.msg .plan-steps > li').length"


def _kind(pack, role: str, to: str) -> dict:
    return preview_plan(pack.model, pack, [parse_step({"kind": "set_role_kind", "role": role, "to": to})], [True])


def test_making_the_approver_an_ai_agent_is_refused_by_the_kind_laws():
    result = _kind(DESK, "Supervisor", "agent")
    assert result["steps"] == [{"status": "applies", "text": "Make Supervisor an AI agent"}]
    assert not result["legal"]
    assert "HUMAN_DECISION:ApproveRefund" in result["codes"]
    assert "Only a person approves a refund: no AI agent, timer or external system holds that decision." in result["laws"]
    assert DESK.role_kind("Supervisor") == "human"  # the pack itself is untouched


def test_a_kind_change_no_law_minds_is_allowed_and_changes_nothing_on_the_state_machine():
    result = _kind(LOAN, "Clerk", "timer")
    assert result["legal"] and result["steps"][0]["text"] == "Make Clerk a timer"
    assert result["candidate_semantic_hash"] == LOAN.model.semantic_hash


def test_a_draft_where_a_kind_law_can_no_longer_be_met_is_refused():
    result = _kind(DESK, "PaymentGateway", "human")  # payouts are confirmed by an external system, and now there is none
    assert not result["legal"] and result["codes"] == ["ROLE_KIND_INVALID"]
    assert "no declared role is of kind system" in result["message"]


def test_an_undeclared_role_or_kind_is_refused():
    result = _kind(DESK, "AutoApprover", "agent")
    assert result["steps"][0]["code"] == "EDIT_INVALID" and not result["legal"]
    with pytest.raises(DomainError):
        parse_step({"kind": "set_role_kind", "role": "Supervisor", "to": "robot"})


@pytest.mark.browser
@pytest.mark.slow
@pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1")
def test_see_and_change_who_holds_a_role_in_a_real_browser():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with ephemeral_eija_server(pack=ROOT / "packs/refund-desk") as server, api.sync_playwright() as playwright:
        executable = os.environ.get("EIJA_CHROMIUM")
        try:
            chrome = (playwright.chromium.launch(headless=True, executable_path=executable) if executable
                      else playwright.chromium.launch(channel="chrome", headless=True))
        except api.Error as exc:
            pytest.skip(f"NOT_RUN: Chrome unavailable: {str(exc).splitlines()[0]}")
        try:
            page = chrome.new_page(viewport={"width": 1600, "height": 900})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)

            # "Who may take it" names each role's kind.
            page.click('.outline button[data-id="transition:TR-PROPOSE"]')
            page.wait_for_selector("#inspector dl")
            assert "SupportAgent (AI agent)" in page.inner_text("#inspector dl")
            assert "Let Supervisor take it" in page.inner_text("#inspector")

            # The actor inspector says who holds the role, and changing it is a step the kind laws judge.
            page.click('.outline button[data-id="role:Supervisor"]')
            picker = page.locator("#inspector label.role-kind select")
            picker.wait_for()
            assert picker.input_value() == "human"
            picker.select_option("agent")
            for _ in range(100):  # the page's CSP rules out wait_for_function with a string
                if page.evaluate(STEPS) == 1 and "refuses" in page.inner_text(".msg .plan-verdict, .msg"):
                    break
                page.wait_for_timeout(100)
            assert page.evaluate(STEPS) == 1
            log = page.inner_text("#chat-log")
            assert "Make Supervisor an AI agent" in log
            assert "Only a person approves a refund" in log

            # A kind the laws do not mind is allowed, and the plan says what it changes.
            page.click("#undo")
            page.click('.outline button[data-id="role:Customer"]')
            page.locator("#inspector label.role-kind select").select_option("agent")
            for _ in range(100):
                if "makes Customer an AI agent" in page.inner_text("#chat-log"):
                    break
                page.wait_for_timeout(100)
            assert "makes Customer an AI agent" in page.inner_text("#chat-log")
            assert page.evaluate("window.PlayIDE.roleKind('Customer')") == "agent"
            assert page.evaluate("window.PlayIDE.inForce('Customer')") == "human"
            assert errors == []
        finally:
            chrome.close()
