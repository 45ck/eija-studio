"""Who can do what (ADR-0171): the role by state matrix, each cell tried in the kernel, a plan's permission changes, and
reachability questions with their three outcomes, including the negative oracles (UNREACHABLE, NOT_SHOWN)."""
from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from eija_studio.application.access import access, matrix, reach
from eija_studio.domain.models import DomainError
from eija_studio.domain.pack import load_pack
from eija_studio.domain.policy import apply_transactions
from eija_studio.domain.transactions import parse_transaction
from eija_studio.interfaces.http import create_app
from kernel_support import harness_studio

ROOT = Path(__file__).resolve().parents[1]
LOAN = load_pack(ROOT / "packs" / "library-loan")
SESSION = "synthetic-access-test"
HEADERS = {"Authorization": "Bearer " + SESSION, "Origin": "http://127.0.0.1:8765"}


def librarian_marks_overdue():
    t = next(t for t in LOAN.model.transitions if t.action == "MarkOverdue")
    return apply_transactions(LOAN.model, [parse_transaction({"kind": "set_role", "transition": t.id, "role": "Librarian"})], LOAN)


def test_every_cell_names_who_the_kernel_lets_through_and_why_the_others_are_refused():
    grid = matrix(LOAN, LOAN.model)
    assert grid["roles"] == ["Member", "Librarian", "Clerk"] and grid["initial"] == "Requested"
    (checkout,) = grid["cells"]["Requested"]["Librarian"]
    assert checkout["action"] == "CheckOut" and checkout["assigned_only"]
    assert {a["actor"]: a["refused"] for a in checkout["actors"]} == {
        "librarian-assigned": None, "librarian-unassigned": "ASSIGNMENT_DENIED", "librarian-revoked": "ACTOR_REVOKED"}
    assert grid["cells"]["Returned"] == {"Member": [], "Librarian": [], "Clerk": []}  # nobody acts from a final state


def test_a_plan_flags_the_permissions_it_adds_and_removes():
    assert access(LOAN, LOAN.model, LOAN.model)["changes"] == {"added": [], "removed": []}
    changes = access(LOAN, librarian_marks_overdue(), LOAN.model)["changes"]
    assert changes == {"added": [{"state": "OnLoan", "role": "Librarian", "action": "MarkOverdue", "to": "Overdue"}],
                       "removed": [{"state": "OnLoan", "role": "Clerk", "action": "MarkOverdue", "to": "Overdue"}]}


def test_unreachable_is_a_proof_over_the_model():
    answer = reach(LOAN, LOAN.model, "Returned", "Librarian")
    assert answer["verdict"] == "UNREACHABLE" and answer["path"] == []
    assert reach(LOAN, LOAN.model, "Overdue", "Clerk")["verdict"] == "UNREACHABLE"


def test_reachable_comes_with_a_path_the_kernel_committed_on_one_record():
    answer = reach(LOAN, librarian_marks_overdue(), "Overdue", "Clerk")
    assert answer["verdict"] == "REACHABLE"
    assert [(s["action"], s["actor"]) for s in answer["path"]] == [("CheckOut", "librarian-assigned"), ("MarkOverdue", "librarian-assigned")]
    assert reach(LOAN, LOAN.model, "Requested", "Member") | {"why": ""} == {
        "target": "Requested", "without": "Member", "model": LOAN.model.semantic_hash, "verdict": "REACHABLE", "path": [], "why": ""}


def test_a_path_no_fixture_actor_can_take_is_not_shown_rather_than_reachable():
    inactive = LOAN.model_copy(update={"fixtures": LOAN.fixtures.model_copy(update={"actors": tuple(
        a.model_copy(update={"active": False}) if a.role == "Clerk" else a for a in LOAN.fixtures.actors)})})
    answer = reach(inactive, inactive.model, "Overdue")
    assert answer["verdict"] == "NOT_SHOWN" and answer["path"] == []


def test_unknown_names_are_refused():
    with pytest.raises(DomainError) as state:
        reach(LOAN, LOAN.model, "Lost")
    with pytest.raises(DomainError) as role:
        reach(LOAN, LOAN.model, "Returned", "Auditor")
    assert (state.value.code, role.value.code) == ("UNKNOWN_STATE", "UNKNOWN_ROLE")


@pytest.fixture
def client(tmp_path):
    app = create_app(harness_studio(tmp_path / "workspace", pack=LOAN), SESSION)
    yield TestClient(app, base_url=HEADERS["Origin"])
    app.state.play.stop()


def test_the_routes_answer_for_the_previewed_plan_and_need_the_session(client):
    t = next(t for t in LOAN.model.transitions if t.action == "MarkOverdue")
    plan = [{"kind": "set_role", "transition": t.id, "role": "Librarian"}]
    assert client.post("/api/play/access", json={}, headers={"Origin": HEADERS["Origin"]}).status_code == 401
    assert client.post("/api/play/access", json={}, headers=HEADERS).json()["changes"] == {"added": [], "removed": []}
    flagged = client.post("/api/play/access", json={"plan": plan}, headers=HEADERS).json()["changes"]
    assert [c["role"] for c in flagged["added"]] == ["Librarian"]
    body = {"plan": plan, "target": "Overdue", "without": "Clerk"}
    assert client.post("/api/play/reach", json=body, headers=HEADERS).json()["verdict"] == "REACHABLE"
    assert client.post("/api/play/reach", json=body | {"plan": None}, headers=HEADERS).json()["verdict"] == "UNREACHABLE"


@pytest.mark.browser
@pytest.mark.slow
@pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1")
def test_the_permissions_tab_asks_the_kernel_and_flags_a_plan_in_a_real_browser():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with ephemeral_eija_server(pack=ROOT / "packs/library-loan") as server, api.sync_playwright() as playwright:
        try:
            executable = os.environ.get("EIJA_CHROMIUM")
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
            page.click("#tab-access")
            page.wait_for_selector(".access-grid")
            page.select_option('.reach select[aria-label="State"]', "Overdue")
            page.select_option('.reach select[aria-label="Without role"]', "Clerk")
            page.click(".reach button.primary")
            page.wait_for_selector(".reach-answer .verdict.ok")  # No: proven over the model
            page.fill("#chat-input", "allow Librarian to MarkOverdue")
            page.click("#chat-send")
            page.wait_for_selector("#chat-log .plan .plan-verdict.ok", timeout=30_000)
            page.click("#chat-log .plan .plan-tools .primary")
            page.click("#tab-access")
            page.wait_for_selector(".reach-path li:nth-child(2)")  # the question is asked again of the preview: Yes, by this path
            assert "Yes" in page.inner_text(".reach-answer .verdict.bad")
            assert "+ Librarian may MarkOverdue from OnLoan" in page.inner_text(".access-changes")
            assert errors == []
        finally:
            chrome.close()
