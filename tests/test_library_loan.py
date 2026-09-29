"""WBS 1.2: the kernel is generic. The library-loan pack (written for this purpose, structurally unlike the excursion
pack) runs through the same runtime and verifier, and its unsafe variant is refused for the right reason.

Negative controls: a receipt made under one pack is refused under another pack's matrix shape; a runtime that
stops enforcing a pack law is caught by the runtime matrix; the sequence law is what refuses the unsafe variant.
"""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

import pytest

from eija_studio.adapters.sqlite_store import SQLiteStore
from eija_studio.application import runtime, verifier
from eija_studio.domain.evidence import assess_receipt, expected_shape
from eija_studio.domain.formal import Context
from eija_studio.domain.laws import Step, evaluate_run
from eija_studio.domain.models import DomainError, ExecuteCommand, Workflow
from eija_studio.domain.pack import load_pack
from eija_studio.domain.policy import check_policy, ensure_policy

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = load_pack(ROOT / "packs" / "library-loan")
EXCURSION = load_pack(ROOT / "packs" / "excursion")
UNSAFE = Workflow.model_validate_json((ROOT / "packs" / "library-loan" / "variants" / "unsafe-return-without-loan.json")
                                      .read_text(encoding="utf-8"))
SUBJECT = {"semantic": "s", "implementation": "i", "policy": "p", "environment": "e", "harness": "h"}


def sandbox_for(root: Path, pack):
    count = []

    @contextmanager
    def sandbox():
        count.append(1)
        yield SQLiteStore(root / f"sb{len(count)}", durability="ephemeral", pack=pack)

    return sandbox


@pytest.fixture(scope="module")
def receipt(tmp_path_factory):
    return verifier.verify_runtime(LIBRARY.model, SUBJECT, sandbox_for(tmp_path_factory.mktemp("loan"), LIBRARY), LIBRARY)


@pytest.fixture
def store(tmp_path):
    return SQLiteStore(tmp_path / "ws", pack=LIBRARY)


def run(store, model, actor, action, state=None):
    with store.transaction() as u:
        item = runtime.initialise(u, "case", model, state=state, pack=LIBRARY)
    command = ExecuteCommand(operation_id=uuid4().hex, actor_id=actor, instance_id=item["id"], action=action, expected_version=0)
    with store.transaction() as u:
        return runtime.execute(u, "case", model, command, pack=LIBRARY)


# ---- runtime ------------------------------------------------------------------------------------------------

def test_a_checkout_runs_with_the_pack_effects_and_recipient(store):
    result = run(store, LIBRARY.model, "librarian-assigned", "CheckOut")
    assert result["instance"]["state"] == "OnLoan" and result["effects"] == ["Audit:LoanCheckedOut", "Notification:MemberNotified"]
    with store.transaction() as u:
        observed = u.observations("case")
    assert [e["kind"] for e in observed["events"]] == ["Audit:LoanCheckedOut"]
    assert [o["kind"] for o in observed["outbox"]] == ["Notification:MemberNotified"] and '"recipient":"member"' in observed["outbox"][0]["body"]


@pytest.mark.parametrize("actor,action,state,code", [
    ("librarian-unassigned", "CheckOut", None, "ASSIGNMENT_DENIED"),
    ("librarian-revoked", "CheckOut", None, "ACTOR_REVOKED"),
    ("member-a", "CheckOut", None, "ROLE_DENIED"),
    ("clerk", "Return", "OnLoan", "ROLE_DENIED"),
    ("member-a", "Cancel", "OnLoan", "STATE_DENIED"),
])
def test_the_runtime_refuses_by_the_pack_table(store, actor, action, state, code):
    with pytest.raises(DomainError) as caught:
        run(store, LIBRARY.model, actor, action, state)
    assert caught.value.code == code


def test_the_unsafe_variant_is_refused_by_the_sequence_law_with_refs(store):
    assert check_policy(UNSAFE, LIBRARY) == ["LOAN_RETURN_WITHOUT_CHECKOUT"]
    with pytest.raises(DomainError) as caught:
        run(store, UNSAFE, "librarian-assigned", "Return")
    assert caught.value.code == "POLICY_BLOCKED"
    assert caught.value.details == {"codes": ["LOAN_RETURN_WITHOUT_CHECKOUT"], "refs": ["law:returned-requires-loan", "state:Returned"]}


def test_evaluate_run_judges_the_sequence_law_on_runs():
    laws = LIBRARY.laws
    good = [Step("CheckOut", "Librarian", "Requested", "OnLoan"), Step("Return", "Librarian", "OnLoan", "Returned")]
    bad = [Step("Return", "Librarian", "Requested", "Returned")]
    actions = {a.id for a in LIBRARY.actions}
    assert evaluate_run(laws, "Requested", good, actions) == []
    assert [v.law for v in evaluate_run(laws, "Requested", bad, actions)] == ["returned-requires-loan"]
    # Per-step laws also bite on runs: a member putting a loan on loan, a step leaving a final state.
    assert {v.law for v in evaluate_run(laws, "Requested", [Step("CheckOut", "Member", "Requested", "OnLoan")], actions)} == {
        "checkout-held-by-librarian", "member-never-lends"}
    assert [v.law for v in evaluate_run(laws, "Requested", [Step("Renew", "Librarian", "Returned", "OnLoan")], actions)] == [
        "returned-final"]


# ---- verifier -----------------------------------------------------------------------------------------------

def test_the_runtime_matrix_covers_the_pack_and_passes(receipt):
    artifact = receipt["artifact"]
    assert artifact["expected_cells"] == len(artifact["cells"]) == 5 * 5 * 6  # actors x states x declared actions (measured)
    assert artifact["matrix"]["actions"] == ["CheckOut", "Cancel", "MarkOverdue", "Return", "ReturnLate", "Renew"]
    assert all(c["expected"] == c["actual"] for c in artifact["cells"])
    accepted = sorted((c["actor"], c["state"], c["action"]) for c in artifact["cells"] if c["actual"]["accepted"])
    assert accepted == [("clerk", "OnLoan", "MarkOverdue"), ("librarian-assigned", "OnLoan", "Return"),
                        ("librarian-assigned", "Overdue", "ReturnLate"), ("librarian-assigned", "Requested", "CheckOut"),
                        ("librarian-unassigned", "OnLoan", "Return"), ("librarian-unassigned", "Overdue", "ReturnLate"),
                        ("member-a", "Requested", "Cancel")]
    context = Context("s", runtime=expected_shape(LIBRARY, LIBRARY.model))
    assert assess_receipt(receipt, SUBJECT, "runtime_matrix", "integration_test", context) == "PASS"


def test_negative_control_a_receipt_for_one_pack_fails_under_another_packs_shape(receipt):
    context = Context("s", runtime=expected_shape(EXCURSION, EXCURSION.model))
    assert assess_receipt(receipt, SUBJECT, "runtime_matrix", "integration_test", context) == "FAIL"


def test_negative_control_a_runtime_that_ignores_assignment_is_caught(tmp_path, monkeypatch):
    original = runtime.check_actor

    def lenient(actor, transition, command):
        original(actor | {"assigned": True}, transition, command)

    monkeypatch.setattr(runtime, "check_actor", lenient)
    broken = verifier.verify_runtime(LIBRARY.model, SUBJECT, sandbox_for(tmp_path, LIBRARY), LIBRARY)
    wrong = [(c["actor"], c["state"], c["action"]) for c in broken["artifact"]["cells"] if c["expected"] != c["actual"]]
    assert wrong == [("librarian-unassigned", "Requested", "CheckOut")]
    context = Context("s", runtime=expected_shape(LIBRARY, LIBRARY.model))
    assert assess_receipt(broken, SUBJECT, "runtime_matrix", "integration_test", context) == "FAIL"


def test_a_workspace_refuses_to_open_with_another_pack(tmp_path):
    SQLiteStore(tmp_path / "ws", pack=LIBRARY)
    with pytest.raises(DomainError) as caught:
        SQLiteStore(tmp_path / "ws", pack=EXCURSION)
    assert caught.value.code == "PACK_MISMATCH"


def test_ensure_policy_details_point_at_laws_and_elements():
    data = EXCURSION.model.model_dump(mode="json")
    next(t for t in data["transitions"] if t["id"] == "TR-APPROVE")["role"] = "Teacher"
    with pytest.raises(DomainError) as caught:
        ensure_policy(Workflow.model_validate(data), EXCURSION)
    assert caught.value.details == {"codes": ["PROTECTED_AUTHORITY:Approve"],
                                    "refs": ["law:approve-held-by-registrar", "transition:TR-APPROVE"]}
