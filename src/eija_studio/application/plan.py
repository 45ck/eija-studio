"""Plan mode for the PlayIDE chat (ADR-0156): an AI proposes a change as numbered typed steps; the person accepts or
rejects each one and sees what the accepted ones would do. Nothing here persists or applies anything.

The proposer's plan is untrusted. Every step is re-parsed into the typed transaction vocabulary, each accepted prefix
is checked for structure step by step (so a step that needs a rejected one says so), and the accepted steps are
applied as one change through the policy (`apply_transactions`), exactly as an owner's edit would be. A plan cannot
choose meaning, approve or apply: making a change real still goes through the change case.
"""
from __future__ import annotations

from typing import Any

from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import Pack
from eija_studio.domain.policy import apply_structural_all, apply_transactions
from eija_studio.domain.transactions import Transaction, parse_transaction
from .diagrams import diff_summary
from .ports import PlanProposer

MAX_STEPS = 12
MAX_REQUEST = 2000


def describe(tx: Transaction, model: Workflow | None = None) -> str:
    """One line a person can check against the diagram. A transition is named by its action, as the diagram labels it,
    when `model` has it; one the same plan adds keeps its id."""
    d = tx.model_dump()
    actions = {t.id: t.action for t in model.transitions} if model is not None else {}
    if "transition" in d:
        d["transition"] = actions.get(d["transition"], d["transition"])
    texts = {
        "add_state": lambda: f"Add state {d['state']}" + (f" after {d['after']}" if d.get("after") else ""),
        "rename_state": lambda: f"Rename state {d['state']} to {d['to']}",
        "remove_state": lambda: f"Remove state {d['state']}",
        "set_initial": lambda: f"Start records in {d['state']}",
        "add_transition": lambda: f"Add {d['action']}: {d['from_state']} → {d['to_state']}, by {d['role']}",
        "retarget_transition": lambda: f"Move the {d['end']} of {d['transition']} to {d['state']}",
        "remove_transition": lambda: f"Remove transition {d['transition']}",
        "set_role": lambda: f"Let {d['role']} take {d['transition']}",
        "set_guards": lambda: f"Set the guards of {d['transition']} to {', '.join(d['guards'])}",
        "set_effects": lambda: f"Set the effects of {d['transition']} to {', '.join(d['required_effects']) or 'none'}",
    }
    return texts[d["kind"]]()


def _steps(document: Any) -> list[tuple[Transaction, str]]:
    if not isinstance(document, dict) or not isinstance(document.get("steps"), list):
        raise DomainError("PLAN_INVALID", "The proposer did not return a plan")
    if not 1 <= len(document["steps"]) <= MAX_STEPS:
        raise DomainError("PLAN_INVALID", f"A plan has 1 to {MAX_STEPS} steps")
    steps = []
    for step in document["steps"]:
        if not isinstance(step, dict):
            raise DomainError("PLAN_INVALID", "A plan step is not an object")
        steps.append((parse_transaction(step.get("transaction")), str(step.get("why", ""))[:300]))
    return steps


def _statuses(model: Workflow, pack: Pack, transactions: list[Transaction], accepted: list[bool]) -> list[dict[str, Any]]:
    """Whether each accepted step applies after the accepted steps before it, with the step in words."""
    kept: list[Transaction] = []
    status: list[dict[str, Any]] = []
    for tx, keep in zip(transactions, accepted, strict=True):
        if not keep:
            status.append({"status": "rejected", "text": describe(tx, model)})
            continue
        try:
            apply_structural_all(model, [*kept, tx], pack)
            kept.append(tx)
            status.append({"status": "applies", "text": describe(tx, model)})
        except DomainError as error:
            status.append({"status": "does_not_apply", "text": describe(tx, model), "code": error.code, "message": error.message})
    return status


def _refusal(error: DomainError, pack: Pack) -> dict[str, Any]:
    """Why the policy refused the accepted steps, with the pack's own words for each law they would break."""
    details = error.details or {}
    refs = details.get("refs", [])
    laws = {f"law:{law.id}": law.description for law in pack.laws}
    return {"codes": details.get("codes", [error.code]), "refs": refs, "message": error.message,
            "laws": [laws[r] for r in refs if r in laws]}


def preview_plan(model: Workflow, pack: Pack, transactions: list[Transaction], accepted: list[bool]) -> dict[str, Any]:
    """What the accepted steps would make of `model`. Each step reports whether it applies after the accepted ones
    before it; the accepted steps together are then checked against the policy as one change."""
    if len(accepted) != len(transactions):
        raise DomainError("PLAN_INVALID", "Accept or reject each step")
    status = _statuses(model, pack, transactions, accepted)
    chosen = [tx for tx, keep in zip(transactions, accepted, strict=True) if keep]
    result: dict[str, Any] = {"steps": status, "accepted": sum(accepted), "legal": False, "codes": [], "refs": [],
                              "candidate": None, "candidate_semantic_hash": None, "diff": None}
    if not chosen or any(s["status"] == "does_not_apply" for s in status):
        return result | {"codes": [] if not chosen else ["PLAN_STEP_DOES_NOT_APPLY"]}
    try:
        candidate = apply_transactions(model, chosen, pack)
    except DomainError as error:
        return result | _refusal(error, pack)
    return result | {"legal": True, "candidate": candidate.model_dump(mode="json"),
                     "candidate_semantic_hash": candidate.semantic_hash, "diff": diff_summary(model, candidate)}


def propose_plan(request: str, model: Workflow, pack: Pack, proposer: PlanProposer) -> dict[str, Any]:
    """Ask the proposer for a plan, re-check it, and preview it with every step accepted."""
    request = request.strip()
    if not 1 <= len(request) <= MAX_REQUEST:
        raise DomainError("PLAN_REQUEST_INVALID", f"Ask in 1 to {MAX_REQUEST} characters")
    document = proposer.propose(request, model, pack)
    steps = _steps(document)
    transactions = [tx for tx, _ in steps]
    return {
        "scope": "plan-proposal", "trust": "UNTRUSTED_PROPOSAL", "request": request, "provider": proposer.name,
        "live": proposer.live, "model": model.semantic_hash, "summary": str(document.get("summary", ""))[:300],
        "meaning": document.get("meaning") if pack.meaning(str(document.get("meaning"))) else None,
        "steps": [{"n": n, "transaction": tx.model_dump(mode="json"), "text": describe(tx, model), "why": why}
                  for n, (tx, why) in enumerate(steps, 1)],
        "preview": preview_plan(model, pack, transactions, [True] * len(transactions)),
    }
