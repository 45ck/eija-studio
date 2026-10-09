"""Plan mode for the PlayIDE chat (ADR-0156): an AI proposes a change as numbered typed steps; the person accepts or
rejects each one and sees what the accepted ones would do. Nothing here persists or applies anything.

The proposer's plan is untrusted. Every step is re-parsed into the typed transaction vocabulary, each accepted prefix
is checked for structure step by step (so a step that needs a rejected one says so), and the accepted steps are
applied as one change through the policy (`apply_transactions`), exactly as an owner's edit would be. A plan cannot
choose meaning, approve or apply: making a change real still goes through the change case.
"""
from __future__ import annotations

from typing import Any

from eija_studio.domain.data import data_for
from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import Pack
from eija_studio.domain.policy import apply_structural_all, apply_transactions
from eija_studio.domain.transactions import AddTransition, Transaction
from .data_steps import DATA_EDITS, DataEdit, FIXED, Step, apply_data, data_changes, describe_data, draft_pack, is_data, parse_step, split, with_kinds, SetRoleKind
from .diagrams import diff_summary
from .new_system import new_names
from .ports import PlanProposer

MAX_STEPS = 12  # steps in one proposal
MAX_DRAFT_STEPS = 64  # steps in the work in progress: every round of a system being built in chat (ADR-0201)
MAX_REQUEST = 2000


def describe(tx: Step, model: Workflow | None = None, pack: Pack | None = None,
             plan: list[Step] | None = None) -> str:
    """One line a person can check against the diagram. A transition is named by its action, as the diagram labels it,
    when `model` has it or a step of the same `plan` adds it. An action or role `pack` does not declare yet is
    called new, so a person sees when a step grows the system's vocabulary (ADR-0201). A data-model step reads as the
    class diagram says it (ADR-0202)."""
    if isinstance(tx, DATA_EDITS):
        return describe_data(tx)
    d = tx.model_dump()
    actions = {t.id: t.action for t in model.transitions} if model is not None else {}
    actions |= {step.id: step.action for step in plan or [] if isinstance(step, AddTransition)}
    if "transition" in d:
        d["transition"] = actions.get(d["transition"], d["transition"])
    return _text(d) + (_new(tx, pack) if pack is not None else "")


def _new(tx: Transaction, pack: Pack) -> str:
    actions, roles = new_names(pack, split([tx])[0])
    names = [f"new action {a}" for a in actions] + [f"new role {r}" for r in roles]
    return f" ({', '.join(names)})" if names else ""


def _text(d: dict[str, Any]) -> str:
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


def _steps(document: Any) -> list[tuple[Step, str]]:
    if not isinstance(document, dict) or not isinstance(document.get("steps"), list):
        raise DomainError("PLAN_INVALID", "The proposer did not return a plan")
    if not 1 <= len(document["steps"]) <= MAX_STEPS:
        raise DomainError("PLAN_INVALID", f"A plan has 1 to {MAX_STEPS} steps")
    steps = []
    for step in document["steps"]:
        if not isinstance(step, dict):
            raise DomainError("PLAN_INVALID", "A plan step is not an object")
        steps.append((parse_step(step.get("transaction")), str(step.get("why", ""))[:300]))
    return steps


def _statuses(model: Workflow, pack: Pack, transactions: list[Step], accepted: list[bool],
              named: Pack | None) -> list[dict[str, Any]]:
    """Whether each accepted step applies after the accepted steps before it, with the step in words. `named` is the
    pack the words call names new against, when the plan may grow the vocabulary. A data-model step applies to the
    data model after the accepted data-model steps before it (ADR-0202)."""
    kept: list[Step] = []
    status: list[dict[str, Any]] = []
    for tx, keep in zip(transactions, accepted, strict=True):
        text = describe(tx, model, named, transactions)
        if not keep:
            status.append({"status": "rejected", "text": text})
            continue
        try:
            _try(model, pack, [*kept, tx], tx)
            kept.append(tx)
            status.append({"status": "applies", "text": text})
        except DomainError as error:
            status.append({"status": "does_not_apply", "text": text, "code": error.code, "message": error.message})
    return status


def _try(model: Workflow, pack: Pack, steps: list[Step], step: Step) -> None:
    transactions, data_steps = split(steps)
    if is_data(step):
        with_kinds(pack, data_steps)
        apply_data(data_for(pack), data_steps)
    else:
        apply_structural_all(model, transactions, pack)


def _refusal(error: DomainError, pack: Pack) -> dict[str, Any]:
    """Why the policy refused the accepted steps, with the pack's own words for each law they would break."""
    details = error.details or {}
    refs = details.get("refs", [])
    laws = {f"law:{law.id}": law.description for law in pack.laws}
    return {"codes": details.get("codes", [error.code]), "refs": refs, "message": error.message,
            "laws": [laws[r] for r in refs if r in laws]}


def preview_plan(model: Workflow, pack: Pack, transactions: list[Step], accepted: list[bool],
                 grows: bool = False) -> dict[str, Any]:
    """What the accepted steps would make of `model`. Each step reports whether it applies after the accepted ones
    before it; the accepted steps together are then checked against the policy as one change. When the system `grows`
    (one you started, ADR-0201), an action or role the accepted steps name is declared as a sketch declares it, and its
    data-model steps change a draft of its class diagram (ADR-0202): `data` is that draft and `data_changes` what changed."""
    if len(accepted) != len(transactions):
        raise DomainError("PLAN_INVALID", "Accept or reject each step")
    chosen = [tx for tx, keep in zip(transactions, accepted, strict=True) if keep]
    result: dict[str, Any] = {"steps": [], "accepted": sum(accepted), "legal": False, "codes": [], "refs": [],
                              "candidate": None, "candidate_semantic_hash": None, "diff": None, "declared": None,
                              "data": None, "data_changes": []}
    try:
        working = draft_pack(pack, split(chosen)[0], grows)
    except DomainError as error:
        return result | {"steps": _statuses(model, pack, transactions, accepted, pack), "codes": [error.code], "message": error.message}
    status = _statuses(model, working, transactions, accepted, pack if grows else None)
    if not grows:
        status = [s | _fixed() if is_data(tx) and s["status"] == "applies" else s for tx, s in zip(transactions, status, strict=True)]
    return _checked(model, working, chosen, result | {"steps": status, "declared": _declared(pack, working)})


def _fixed() -> dict[str, Any]:
    return {"status": "does_not_apply", "code": "PLAN_DATA_FIXED", "message": FIXED}


def _checked(model: Workflow, pack: Pack, chosen: list[Step], result: dict[str, Any]) -> dict[str, Any]:
    """The preview once every step has its status: the accepted steps together, checked by the policy as one change,
    with the accepted data-model steps applied to the data model."""
    status = result["steps"]
    if not chosen or any(s["status"] == "does_not_apply" for s in status):
        return result | {"codes": [] if not chosen else ["PLAN_STEP_DOES_NOT_APPLY"]}
    transactions, data_steps = split(chosen)
    try:
        candidate = apply_transactions(model, transactions, pack) if transactions else model
    except DomainError as error:
        return result | _refusal(error, pack)
    result = result | _drafted(pack, data_steps)
    return result | {"legal": True, "candidate": candidate.model_dump(mode="json"),
                     "candidate_semantic_hash": candidate.semantic_hash, "diff": diff_summary(model, candidate)}


def _drafted(pack: Pack, data_steps: list[DataEdit]) -> dict[str, Any]:
    """The class diagram as the plan's data-model steps leave it, and who holds each role as its kind steps leave it."""
    found: dict[str, Any] = {}
    before = data_for(pack)
    after = apply_data(before, data_steps)
    if data_steps and after is not None:
        found |= {"data": after.model_dump(mode="json"), "data_changes": data_changes(before, after)}
    if any(isinstance(s, SetRoleKind) for s in data_steps):
        found["kinds"] = {r.id: r.kind for r in with_kinds(pack, data_steps).roles}  # #156
    return found


def _declared(before: Pack, after: Pack) -> dict[str, list[str]] | None:
    """The actions and roles `after` declares that `before` does not."""
    actions = [a.id for a in after.actions if before.action(a.id) is None]
    roles = [r.id for r in after.roles if r.id not in {x.id for x in before.roles}]
    return {"actions": actions, "roles": roles} if actions or roles else None


def example_passes(request: str, model: Workflow, pack: Pack, proposer: PlanProposer | None) -> bool:
    """Whether `request`, sent to the chat as it stands, becomes a plan the policy allows on `model`. Only an offline
    proposer is asked: a live one would spend a model call on every page load, so it gets typed steps instead."""
    if proposer is None or proposer.live or not request.strip():
        return False
    try:
        return bool(propose_plan(request, model, pack, proposer)["preview"]["legal"])
    except DomainError:
        return False


def propose_plan(request: str, model: Workflow, pack: Pack, proposer: PlanProposer, grows: bool = False) -> dict[str, Any]:
    """Ask the proposer for a plan, re-check it, and preview it with every step accepted. `model` may already carry
    earlier rounds of the same work in progress (ADR-0201): the new steps are planned on top of it. When the system
    `grows`, the proposer may name new states, actions and roles, and the preview declares them."""
    request = request.strip()
    if not 1 <= len(request) <= MAX_REQUEST:
        raise DomainError("PLAN_REQUEST_INVALID", f"Ask in 1 to {MAX_REQUEST} characters")
    document = proposer.propose(request, model, pack, grows=True) if grows else proposer.propose(request, model, pack)
    steps = _steps(document)
    transactions = [tx for tx, _ in steps]
    return {
        "scope": "plan-proposal", "trust": "UNTRUSTED_PROPOSAL", "request": request, "provider": proposer.name,
        "live": proposer.live, "model": model.semantic_hash, "summary": str(document.get("summary", ""))[:300],
        "meaning": document.get("meaning") if pack.meaning(str(document.get("meaning"))) else None,
        "steps": [{"n": n, "transaction": tx.model_dump(mode="json"), "text": describe(tx, model, pack if grows else None, transactions),
                   "why": why} for n, (tx, why) in enumerate(steps, 1)],
        "preview": preview_plan(model, pack, transactions, [True] * len(transactions), grows),
    }
