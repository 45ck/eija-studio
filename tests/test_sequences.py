"""Sequence diagrams the kernel checks (ADR-0185): every message of a scenario is run through `runtime.execute`, so a
sequence the model can't produce is flagged at the message the kernel refuses, a neg must be refused, and a change shows
the scenarios it breaks or fixes. Negative oracles included: refused messages, a neg the kernel lets through, a wrong
refusal code, an unreachable message, and malformed documents."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from eija_studio.application.sequences import MAX_PATHS, check_sequences, default_sequences, sequences_for
from eija_studio.domain.models import DomainError
from eija_studio.domain.pack import load_pack
from eija_studio.domain.policy import apply_transactions
from eija_studio.domain.sequences import parse_sequences
from eija_studio.domain.transactions import parse_transaction
from eija_studio.interfaces.http import create_app
from kernel_support import harness_studio

ROOT = Path(__file__).resolve().parents[1]
LOAN = load_pack(ROOT / "packs" / "library-loan")
DOCUMENT = json.loads((ROOT / "packs" / "library-loan" / "sequences.json").read_text(encoding="utf-8"))
SESSION = "synthetic-sequences-test"
HEADERS = {"Authorization": "Bearer " + SESSION, "Origin": "http://127.0.0.1:8765"}


def one(steps, records=("loan",)):
    return parse_sequences({"id": "library-loan", "sequences": [{"id": "s", "title": "S", "records": list(records), "steps": steps}]}, "library-loan")


def msg(actor, action, record=""):
    return {"actor": actor, "action": action, "record": record}


def neg(*steps, refused=None):
    return {"fragment": "neg", "refused": refused, "operands": [{"guard": "", "steps": list(steps)}]}


def checked(document, model=LOAN.model, base=None):
    return check_sequences(LOAN, model, document, base)


def by_ref(sequence):
    return {m["ref"]: m for m in sequence["messages"]}


def clerk_returns_late():
    t = next(t for t in LOAN.model.transitions if t.action == "ReturnLate")
    return apply_transactions(LOAN.model, [parse_transaction({"kind": "set_role", "transition": t.id, "role": "Clerk"})], LOAN)


def test_the_packs_sequences_are_produced_by_the_kernel_with_states_effects_and_refused_negs():
    document, source = sequences_for(LOAN, LOAN.model)
    report = checked(document)
    assert source == "pack" and report["status"] == "PRODUCIBLE" and report["counts"] == {"producible": 3, "broken": 0}
    lend = by_ref(report["sequences"][0])
    assert [(r, m["verdict"], m["states"]) for r, m in lend.items()] == [
        ("0", "OK", ["OnLoan"]), ("1.0.0", "OK", ["Returned"]), ("1.1.0", "OK", ["Overdue"]), ("1.1.1", "OK", ["Returned"])]
    assert lend["0"]["effects"] == ["Audit:LoanCheckedOut", "Notification:MemberNotified"]  # the kernel's own effects
    who = report["sequences"][1]
    assert [(f["verdict"], f["code"]) for f in who["fragments"]] == [
        ("HOLDS", "ROLE_DENIED"), ("HOLDS", "ASSIGNMENT_DENIED"), ("HOLDS", "ACTOR_REVOKED"), ("HOLDS", "ROLE_DENIED")]
    assert [r["label"] for r in who["replies"]] == ["refused: ROLE_DENIED", "refused: ASSIGNMENT_DENIED", "refused: ACTOR_REVOKED", "refused: ROLE_DENIED"]


def test_a_message_the_model_cant_produce_is_flagged_where_the_kernel_refuses_it_and_the_rest_is_not_reached():
    for message, code, why in [
        (msg("librarian-assigned", "Renew"), "ACTION_DENIED", "Renew is not in the model"),
        (msg("member-a", "CheckOut"), "ROLE_DENIED", "member-a is a Member; CheckOut is for a Librarian"),
        (msg("librarian-assigned", "Return"), "STATE_DENIED", "Return does not leave Requested"),
        (msg("nobody", "CheckOut"), "UNKNOWN_ACTOR", "nobody is not one of the pack's actors"),
    ]:
        sequence = checked(one([message, msg("librarian-assigned", "CheckOut")]))["sequences"][0]
        first, second = by_ref(sequence)["0"], by_ref(sequence)["1"]
        assert (sequence["verdict"], first["verdict"], first["code"], first["why"]) == ("BROKEN", "BROKEN", code, why)
        assert second["verdict"] == "NOT_REACHED" and sequence["first_problem"] == why
        assert sequence["replies"][0]["tone"] == "bad" and not sequence["invariants"]


def test_a_neg_the_kernel_lets_through_or_refuses_for_another_reason_is_broken():
    allowed = checked(one([neg(msg("librarian-assigned", "CheckOut"))]))["sequences"][0]
    assert allowed["verdict"] == "BROKEN" and allowed["fragments"][0]["verdict"] == "BROKEN"
    assert by_ref(allowed)["0.0.0"]["verdict"] == "COMMITTED"
    wrong = checked(one([neg(msg("member-a", "CheckOut"), refused="STATE_DENIED")]))["sequences"][0]["fragments"][0]
    assert (wrong["verdict"], wrong["code"]) == ("BROKEN", "ROLE_DENIED")
    # A neg is undone: what it tried does not move the record, so the next message starts where it was.
    after = checked(one([neg(msg("librarian-assigned", "CheckOut"), msg("clerk", "Return")), msg("librarian-assigned", "CheckOut")]))
    assert by_ref(after["sequences"][0])["1"]["verdict"] == "OK"


def test_alt_and_opt_are_checked_on_every_trace_and_a_failure_names_its_trace():
    late = {"fragment": "alt", "operands": [{"guard": "on time", "steps": [msg("librarian-assigned", "Return")]},
                                             {"guard": "late", "steps": [msg("clerk", "MarkOverdue")]}]}
    sequence = checked(one([msg("librarian-assigned", "CheckOut"), late, msg("librarian-assigned", "ReturnLate")]))["sequences"][0]
    last = by_ref(sequence)["2"]
    assert (last["verdict"], last["code"]) == ("BROKEN", "STATE_DENIED") and last["via"] == ["alt [on time]"]
    assert "on the trace alt [on time]" in last["why"]
    optional = {"fragment": "opt", "operands": [{"guard": "overdue", "steps": [msg("clerk", "MarkOverdue")]}]}
    skipped = checked(one([msg("librarian-assigned", "CheckOut"), optional, msg("librarian-assigned", "Return")]))["sequences"][0]
    assert by_ref(skipped)["2"]["via"] == ["opt [overdue]"]  # Return works without the opt, not after it


def test_a_change_shows_the_scenarios_it_breaks_and_fixes_and_ripples():
    report = checked(sequences_for(LOAN, LOAN.model)[0], clerk_returns_late(), LOAN.model)
    lend = report["sequences"][0]
    assert report["changed"] and (lend["verdict"], lend["was"], lend["change"]) == ("BROKEN", "PRODUCIBLE", "breaks")
    late = by_ref(lend)["1.1.1"]
    assert (late["verdict"], late["was"], late["change"], late["code"]) == ("BROKEN", "OK", "changed", "ROLE_DENIED")
    assert by_ref(lend)["0"]["change"] == "same"
    renew = one([msg("librarian-assigned", "CheckOut"), msg("clerk", "MarkOverdue"), msg("librarian-assigned", "Renew")])
    t = next(t for t in LOAN.model.transitions if t.action == "MarkOverdue")
    renewing = apply_transactions(LOAN.model, [parse_transaction({"kind": "add_transition", "id": "TR-RENEW", "action": "Renew",
                                                                   "from_state": t.to_state, "to_state": "OnLoan", "role": "Librarian"})], LOAN)
    fixed = checked(renew, renewing, LOAN.model)["sequences"][0]
    assert (fixed["verdict"], fixed["was"], fixed["change"], by_ref(fixed)["2"]["change"]) == ("PRODUCIBLE", "BROKEN", "fixes", "added")


def test_every_pack_gets_producible_default_scenarios_from_its_model():
    for name in ("library-loan", "excursion", "eija-review-slice"):
        pack = load_pack(ROOT / "packs" / name)
        first, again = default_sequences(pack, pack.model), default_sequences(pack, pack.model)
        assert first == again and first.sequences  # deterministic
        report = check_sequences(pack, pack.model, first)
        assert report["status"] == "PRODUCIBLE", report["sequences"]
        assert any(f["operator"] == "neg" and f["verdict"] == "HOLDS" for s in report["sequences"] for f in s["fragments"])


def test_the_layout_puts_lifelines_in_columns_and_rows_top_to_bottom():
    sequence = checked(sequences_for(LOAN, LOAN.model)[0])["sequences"][0]
    xs = [lifeline["x"] for lifeline in sequence["lifelines"]]
    assert xs == sorted(set(xs)) and [lifeline["kind"] for lifeline in sequence["lifelines"]] == ["actor", "actor", "record", "effect", "effect"]
    ys = [m["y"] for m in sequence["messages"]]
    assert ys == sorted(ys) and len(set(ys)) == len(ys) and max(ys) < sequence["height"]
    frame = sequence["fragments"][0]
    inside = [m for m in sequence["messages"] if m["ref"].startswith("1.")]
    assert all(frame["y0"] < m["y"] < frame["y1"] for m in inside) and frame["operands"][1]["y"] > inside[0]["y"]


def test_sequences_export_through_the_existing_mermaid_and_plantuml_emitters():
    sequences = checked(sequences_for(LOAN, LOAN.model)[0])["sequences"]
    mermaid, plantuml = sequences[0]["export"]["mermaid"], sequences[1]["export"]["plantuml"]
    assert "alt returned on time" in mermaid and "else kept too long" in mermaid and "librarian_assigned->>loan: CheckOut()" in mermaid
    assert "group neg [a member lends to themselves]" in plantuml and "loan --> member_a : refused: ROLE_DENIED" in plantuml


def test_malformed_documents_are_refused_with_stable_codes():
    bad = copy.deepcopy(DOCUMENT)
    bad["sequences"][0]["steps"][1]["operands"].pop()  # an alt with one operand
    for document, code in [(bad, "SEQUENCES_INVALID"), (DOCUMENT | {"id": "excursion"}, "SEQUENCES_PACK_MISMATCH"),
                           (DOCUMENT | {"sequences": DOCUMENT["sequences"] * 2}, "SEQUENCES_INVALID")]:
        with pytest.raises(DomainError) as refused:
            parse_sequences(document, "library-loan")
        assert refused.value.code == code
    with pytest.raises(DomainError) as unknown:
        one([msg("member-a", "Cancel", "book")])
    assert unknown.value.code == "SEQUENCES_INVALID" and "book" in unknown.value.message
    branchy = {"fragment": "opt", "operands": [{"guard": "", "steps": [msg("member-a", "Cancel")]}]}
    with pytest.raises(DomainError) as many:
        checked(one([branchy] * 7))  # 2^7 traces
    assert many.value.code == "SEQUENCE_TOO_BRANCHY" and MAX_PATHS < 2 ** 7


@pytest.fixture
def client(tmp_path):
    studio = harness_studio(tmp_path / "workspace", pack=LOAN)
    app = create_app(studio, SESSION)
    yield TestClient(app, base_url=HEADERS["Origin"]), studio
    app.state.play.stop()


def test_the_route_checks_the_shown_model_against_the_model_in_force_and_saves_nothing(client):
    client, studio = client
    with studio.store.transaction() as u:
        before = u.active()["model"]
    assert client.post("/api/play/sequences", json={}, headers={"Origin": HEADERS["Origin"]}).status_code == 401
    plain = client.post("/api/play/sequences", json={}, headers=HEADERS).json()
    assert (plain["source"], plain["status"], plain["changed"]) == ("pack", "PRODUCIBLE", False)
    t = next(t for t in LOAN.model.transitions if t.action == "ReturnLate")
    plan = [{"kind": "set_role", "transition": t.id, "role": "Clerk"}]
    planned = client.post("/api/play/sequences", json={"plan": plan}, headers=HEADERS).json()
    assert planned["changed"] and planned["sequences"][0]["change"] == "breaks"
    edited = client.post("/api/play/sequences", json={"sequences": one([msg("librarian-assigned", "Renew")]).model_dump(mode="json")}, headers=HEADERS).json()
    assert (edited["source"], edited["status"]) == ("edited", "BROKEN")
    malformed = client.post("/api/play/sequences", json={"sequences": {"id": "library-loan", "sequences": []}}, headers=HEADERS).json()
    assert malformed["code"] == "SEQUENCES_INVALID"
    ripple = client.post("/api/play/ripple", json={"plan": plan}, headers=HEADERS).json()
    assert [i["code"] for i in ripple["diagrams"]["sequences"]] == ["SEQUENCE_BROKEN"]
    with studio.store.transaction() as u:
        assert u.active()["model"] == before
    page = client.get("/play").text
    assert "/assets/play-sequence.js" in page and client.get("/assets/play-sequence.js").status_code == 200
    assert client.get("/assets/play-sequence.css").status_code == 200


@pytest.mark.browser
@pytest.mark.slow
@pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1")
def test_the_sequences_tab_draws_flags_and_edits_in_a_real_browser():
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
            page.click("#tab-sequences")
            page.wait_for_selector(".seq-verdict.ok")
            assert page.evaluate("PlaySequence.result().sequences.length") == 3
            page.select_option("#seq-actor", "librarian-assigned")
            page.select_option("#seq-action", "Renew")
            page.click("#seq-add button")
            page.wait_for_selector(".seq-verdict.bad")  # Renew is not in the model: flagged where the kernel refused it
            assert "Renew is not in the model" in page.inner_text("#seq-verdict")
            assert page.inner_text("#tab-sequences .badge") == "✗ 1"
            assert "Can't be produced: ACTION_DENIED" in page.inner_text("#inspector")
            assert errors == []
        finally:
            chrome.close()
