"""Hand-declared activation expectations exercised against disposable SQLite workspaces.

Only the synthetic factory marks a test identity trusted. No existing workspace, launch
capability, owner decision, key, source fixture or connected source is read or changed.
The candidate fixture is written independently of the transaction interpreter.
"""
from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from eija_studio.adapters.identity import PACKAGE, identity
from eija_studio.application.service import Studio
from eija_studio.bootstrap import build_studio
from eija_studio.domain.change_case import OwnerPlanRequest
from eija_studio.domain.models import AGENT, DomainError, LayoutChange, Principal, Workflow, fingerprint
from eija_studio.domain.pack import Pack, load_pack
from eija_studio.domain.transactions import RetargetTransition

TEST_OWNER = Principal(id="activation-check-owner", capabilities=frozenset({"select", "edit", "approve", "apply"}))
HARNESS_MARK = "activation-selfdogfood-synthetic-owner"
StudioFactory = Callable[[Path], Studio]

ORACLE_PATH = PACKAGE.parents[1] / "tests/fixtures/activation-selfdogfood.json"
FIXTURE = json.loads(ORACLE_PATH.read_text(encoding="utf-8"))
# Independently declared fixture data, not copied from pack.meaning() or generated from
# the service result. Generic checker code owns no domain vocabulary.
STEPS = tuple(FIXTURE["steps"])


def fixture_pack() -> Pack:
    return load_pack(PACKAGE.parents[1] / "packs" / FIXTURE["pack"])


def ensure(condition: bool, reason: str) -> None:
    if not condition:
        raise AssertionError(reason)


def synthetic_studio(directory: Path, *, cls: type[Studio] = Studio) -> Studio:
    """Actual adapters/services; only a freshly created synthetic workspace gets this test identity."""
    studio = build_studio(directory, pack=fixture_pack())
    studio.__class__ = cls
    # A synthetic caller can test the mechanics. This never restamps measured identity.
    measured = identity(studio.pack)
    studio.identity_provider = lambda: measured | {"trusted_fixture": True, "identity_source": HARNESS_MARK}
    return studio


def expected_candidate() -> Workflow:
    """Explicit output oracle for the five commands above; no second interpreter."""
    return Workflow.model_validate(FIXTURE["expected_candidate"])


def plan_request(studio: Studio) -> OwnerPlanRequest:
    with studio.store.transaction() as session:
        active = session.active()
    return OwnerPlanRequest.model_validate({
        "request": FIXTURE["request"],
        "pack_id": studio.pack.id, "expected_pack_digest": studio.pack.digest,
        "expected_baseline_version": active["version"],
        "expected_baseline_semantic_hash": Workflow.model_validate(active["model"]).semantic_hash,
        "expected_candidate_semantic_hash": expected_candidate().semantic_hash,
        "steps": [{"transaction": tx, "author": "ai" if index < 4 else "you",
                   "round": 1 if index < 4 else 2, "request": FIXTURE["round_requests"][int(index >= 4)]}
                  for index, tx in enumerate(STEPS)],
    })


def snapshot(studio: Studio) -> dict[str, Any]:
    with studio.store.transaction() as session:
        active = session.active()
        counts = session.effect_counts()
    return {"active": active, "cases": studio.store.list_cases(), "counts": counts}


def refused(call: Callable[[], Any], code: str) -> str:
    try:
        call()
    except DomainError as error:
        ensure(error.code == code, f"Expected {code}; observed {error.code}")
        return error.code
    raise AssertionError(f"Expected {code}; operation unexpectedly accepted")


def selected(studio: Studio) -> dict[str, Any]:
    return studio.from_plan(plan_request(studio), TEST_OWNER)


def verified(studio: Studio) -> dict[str, Any]:
    case = selected(studio)
    return studio.verify(case["id"], case["version"])


def approval(studio: Studio, case: dict[str, Any], principal: Principal = TEST_OWNER) -> dict[str, Any]:
    packet = studio.view(case["id"])["packet"]
    return studio.approve(case["id"], case["version"], packet["subject_hash"],
                          {question["id"]: question["expected"] for question in packet["questions"]}, True, principal)


def exact_plan(studio: Studio) -> dict[str, Any]:
    before = snapshot(studio)
    command = plan_request(studio)
    case = studio.from_plan(command, TEST_OWNER)
    ensure(Workflow.model_validate(case["candidate"]) == expected_candidate(), "Exact reviewed candidate was lost")
    ensure(case["transactions"] == list(STEPS), "Typed commands were replaced or reordered")
    ensure(case["selection"]["steps"] == command.model_dump(mode="json")["steps"], "Authorship or rounds were lost")
    ensure(case["selected_by"] == TEST_OWNER.id, "Selected owner does not match the test principal")
    ensure(snapshot(studio)["active"] == before["active"], "Transfer changed the active model")
    history = studio.history(case["id"])
    ensure(history["status"] == "ready", "Owner plan does not replay in semantic history")
    return {"candidate_semantic_hash": expected_candidate().semantic_hash, "commands": len(STEPS),
            "selection_kind": case["selection"]["kind"], "active_version": before["active"]["version"]}


def candidate_binding(studio: Studio) -> dict[str, Any]:
    before = snapshot(studio)
    command = plan_request(studio).model_copy(update={"expected_candidate_semantic_hash": "0" * 64})
    code = refused(lambda: studio.from_plan(command, TEST_OWNER), "CANDIDATE_CHANGED")
    ensure(snapshot(studio) == before, "Refused candidate identity still persisted a case or effect")
    return {"code": code, "unchanged": True}


def stale_plan(studio: Studio) -> dict[str, Any]:
    before = snapshot(studio)
    command = plan_request(studio).model_copy(update={"expected_baseline_version": 1})
    code = refused(lambda: studio.from_plan(command, TEST_OWNER), "STALE_BASELINE")
    ensure(snapshot(studio) == before, "Stale transfer changed the workspace")
    return {"code": code, "unchanged": True}


def agent_plan(studio: Studio) -> dict[str, Any]:
    before = snapshot(studio)
    code = refused(lambda: studio.from_plan(plan_request(studio), AGENT), "AUTHORITY_REQUIRED")
    ensure(snapshot(studio) == before, "Agent transfer changed the workspace")
    return {"code": code, "unchanged": True}


def agent_select(studio: Studio) -> dict[str, Any]:
    case = studio.create(FIXTURE["supported_request"])
    case = studio.propose(case["id"], case["version"])
    before = snapshot(studio)
    code = refused(lambda: studio.select(case["id"], case["version"], FIXTURE["supported_meaning"], AGENT), "AUTHORITY_REQUIRED")
    ensure(snapshot(studio) == before, "Agent meaning selection changed the workspace")
    return {"code": code, "unchanged": True}


def agent_approve(studio: Studio) -> dict[str, Any]:
    case = verified(studio)
    before = snapshot(studio)
    code = refused(lambda: approval(studio, case, AGENT), "AUTHORITY_REQUIRED")
    ensure(snapshot(studio) == before, "Agent approval created a decision")
    return {"code": code, "unchanged": True}


def agent_apply(studio: Studio) -> dict[str, Any]:
    case = approval(studio, verified(studio))
    before = snapshot(studio)
    code = refused(lambda: studio.apply(case["id"], case["version"], AGENT), "AUTHORITY_REQUIRED")
    ensure(snapshot(studio) == before, "Agent activation changed the baseline")
    return {"code": code, "unchanged": True}


def source_review(studio: Studio) -> dict[str, Any]:
    case = selected(studio)
    measured = studio.identity_provider()
    studio.identity_provider = lambda: measured | {"trusted_fixture": False, "identity_source": "negative-source-control"}
    before = snapshot(studio)
    code = refused(lambda: studio.verify(case["id"], case["version"]), "SOURCE_REVIEW_REQUIRED")
    ensure("SOURCE_REVIEW_REQUIRED" in studio.view(case["id"])["packet"]["blockers"], "Source-review blocker is hidden")
    ensure(snapshot(studio) == before, "Source-blocked verification persisted receipts")
    return {"code": code, "unchanged": True}


def stale_evidence(studio: Studio) -> dict[str, Any]:
    case = verified(studio)
    receipts = fingerprint(case["receipts"])
    measured = studio.identity_provider()
    studio.identity_provider = lambda: measured | {"implementation": "changed-implementation-identity"}
    packet = studio.view(case["id"])["packet"]
    ensure(packet["technical_claims"]["runtime_matrix"] == "STALE", "Changed source reused current evidence")
    ensure(not packet["eligible"], "Stale runtime evidence remained eligible")
    ensure(fingerprint(studio.view(case["id"])["case"]["receipts"]) == receipts, "Receipt payload was rewritten")
    before = snapshot(studio)
    code = refused(lambda: approval(studio, case), "GATE_BLOCKED")
    ensure(snapshot(studio) == before, "Stale evidence created a decision")
    return {"code": code, "runtime_matrix": "STALE", "receipts_unchanged": True}


def changed_review_subject(studio: Studio) -> dict[str, Any]:
    case = verified(studio)
    old = studio.view(case["id"])["packet"]
    case = studio.layout(case["id"], case["version"], LayoutChange(node=FIXTURE["anchor_state"], x=9, y=8), TEST_OWNER)
    before = snapshot(studio)
    code = refused(lambda: studio.approve(case["id"], case["version"], old["subject_hash"],
                                         {q["id"]: q["expected"] for q in old["questions"]}, True, TEST_OWNER),
                   "SUBJECT_CHANGED")
    ensure(snapshot(studio) == before, "Stale review created a decision")
    return {"code": code, "unchanged": True}


def edit_invalidation(studio: Studio) -> dict[str, Any]:
    case = approval(studio, verified(studio))
    before_receipts = fingerprint(case["receipts"])
    case = studio.edit(case["id"], case["version"],
                       RetargetTransition(kind="retarget_transition", transition=FIXTURE["edited_transition"],
                                          end="source", state=FIXTURE["changed_state"]),
                       TEST_OWNER)
    packet = studio.view(case["id"])["packet"]
    ensure(case["decision"] is None, "Material edit retained approval")
    ensure(packet["technical_claims"]["runtime_matrix"] == "STALE", "Material edit retained current runtime evidence")
    ensure(fingerprint(case["receipts"]) == before_receipts, "Edit rewrote original receipts")
    code = refused(lambda: studio.apply(case["id"], case["version"], TEST_OWNER), "GATE_BLOCKED")
    return {"code": code, "decision_cleared": True, "receipts_unchanged": True}


def competing_activation(studio: Studio) -> dict[str, Any]:
    first = approval(studio, verified(studio))
    second = approval(studio, verified(studio))
    studio.apply(first["id"], first["version"], TEST_OWNER)
    before = snapshot(studio)
    code = refused(lambda: studio.apply(second["id"], second["version"], TEST_OWNER), "GATE_BLOCKED")
    ensure(snapshot(studio) == before, "Competing activation silently overwrote the baseline")
    ensure("STALE_BASELINE" in studio.view(second["id"])["packet"]["blockers"], "Competing baseline is not identified")
    return {"code": code, "blocker": "STALE_BASELINE", "active_version": 1}


def stale_case_cas(studio: Studio) -> dict[str, Any]:
    """Exercise the actual adapter CAS beneath the aggregate's earlier version check."""
    case = selected(studio)
    stale = dict(case)
    current = studio.layout(case["id"], case["version"], LayoutChange(node=FIXTURE["anchor_state"], x=3, y=4), TEST_OWNER)
    before = snapshot(studio)

    def write_stale() -> None:
        with studio.store.transaction() as session:
            session.save_case(stale, case["version"])

    code = refused(write_stale, "STALE_VERSION")
    ensure(snapshot(studio) == before, "Stale adapter write lost the newer case")
    return {"code": code, "case_version": current["version"], "unchanged": True}


def atomic_rollback(studio: Studio) -> dict[str, Any]:
    """Crash between baseline update and case save through the actual apply callable."""
    case = approval(studio, verified(studio))
    before = snapshot(studio)

    class InjectedFailure(RuntimeError):
        pass

    original = studio._save

    def fail_save(*args: Any, **kwargs: Any) -> dict[str, Any]:
        if args[2].get("stage") == "APPLIED":
            raise InjectedFailure("Synthetic failure after active update")
        return original(*args, **kwargs)

    studio._save = fail_save
    try:
        studio.apply(case["id"], case["version"], TEST_OWNER)
    except InjectedFailure:
        pass
    else:
        raise AssertionError("Injected activation failure did not interrupt apply")
    finally:
        studio._save = original
    ensure(snapshot(studio) == before, "Failed activation retained partial baseline, case or event")
    return {"failure_point": "after_set_active_before_case_save", "unchanged": True}


def restart_and_duplicate(studio: Studio) -> dict[str, Any]:
    case = approval(studio, verified(studio))
    applied = studio.apply(case["id"], case["version"], TEST_OWNER)
    before = snapshot(studio)
    reopened = synthetic_studio(studio.store.directory)
    ensure(snapshot(reopened) == before, "Restart changed activation history or baseline")
    ensure(Workflow.model_validate(reopened.workbench()["model"]) == expected_candidate(), "Reopened workbench has an old model")
    ensure(reopened.view(case["id"])["case"]["stage"] == "APPLIED", "Applied case did not survive restart")
    code = refused(lambda: reopened.apply(case["id"], applied["version"], TEST_OWNER), "CASE_CLOSED")
    ensure(snapshot(reopened) == before, "Duplicate activation changed the baseline or audit")
    new = reopened.create("Inspect the active revision")
    ensure(Workflow.model_validate(new["baseline"]) == expected_candidate(), "Next case used the original pack model")
    return {"code": code, "active_version": 1, "new_case_baseline_matches": True, "restart": "new SQLite connections"}


CHECKS: dict[str, Callable[[Studio], dict[str, Any]]] = {
    "exact_plan_transfer": exact_plan,
    "candidate_identity_binding": candidate_binding,
    "stale_plan_transfer": stale_plan,
    "agent_plan_denied": agent_plan,
    "agent_select_denied": agent_select,
    "agent_approve_denied": agent_approve,
    "agent_apply_denied": agent_apply,
    "source_review_required": source_review,
    "stale_evidence_denied": stale_evidence,
    "stale_review_subject_denied": changed_review_subject,
    "edit_invalidates_evidence_and_decision": edit_invalidation,
    "competing_activation_denied": competing_activation,
    "stale_case_adapter_cas": stale_case_cas,
    "activation_atomic_rollback": atomic_rollback,
    "activation_restart_and_duplicate": restart_and_duplicate,
}
