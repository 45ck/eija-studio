"""Affordance map (WBS 1.3): which single edits the kernel would accept, and why the others are refused.

For every transition end x state, and every transition x declared role, the edit is DRY-RUN through the same
``policy.apply_transactions`` a real edit uses, so "legal" here means exactly "the edit endpoint would accept it"
and an illegal entry lists exactly the codes and refs that edit would be refused with. Nothing is written.
"""
from __future__ import annotations

from typing import Any, Literal

from .models import DomainError, Workflow
from .pack import Pack
from .policy import apply_transactions
from .transactions import RetargetTransition, SetRole, Transaction


def dry_run(model: Workflow, tx: Transaction, pack: Pack) -> dict[str, Any]:
    """{legal, codes, refs} of applying ``tx`` to ``model`` under ``pack``, without applying it anywhere."""
    try:
        apply_transactions(model, (tx,), pack)
    except DomainError as error:
        details = error.details or {}
        return {"legal": False, "codes": list(details.get("codes") or [error.code]), "refs": list(details.get("refs") or [])}
    return {"legal": True, "codes": [], "refs": []}


def _entry(model: Workflow, pack: Pack, tx: Transaction, element: str, kind: str, target: str) -> dict[str, Any]:
    return {"element": element, "kind": kind, "target": target, "transaction": tx.model_dump(mode="json")} | dry_run(model, tx, pack)


def _retargets(model: Workflow, pack: Pack) -> list[dict[str, Any]]:
    found = []
    for t in model.transitions:
        ends: tuple[tuple[Literal["source", "target"], str], ...] = (("source", t.from_state), ("target", t.to_state))
        for end, current in ends:
            found += [_entry(model, pack, RetargetTransition(kind="retarget_transition", transition=t.id, end=end, state=s),
                             "transition:" + t.id, "retarget_" + end, "state:" + s)
                      for s in model.states if s != current]
    return found


def _roles(model: Workflow, pack: Pack) -> list[dict[str, Any]]:
    return [_entry(model, pack, SetRole(kind="set_role", transition=t.id, role=r.id), "transition:" + t.id, "set_role", "role:" + r.id)
            for t in model.transitions for r in pack.roles if r.id != t.role]


def affordances(model: Workflow, pack: Pack) -> list[dict[str, Any]]:
    """Every single-step retarget and role change of ``model``, each with its dry-run verdict."""
    return _retargets(model, pack) + _roles(model, pack)
