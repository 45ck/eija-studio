"""Semantic history is a projection of typed commands, replayed by the existing policy interpreter.

The selected meaning is one protected atomic batch. Owner edits and undone edits are individual
commands. These reconstructed models are not historical verification receipts or case snapshots.
"""
from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from eija_studio.domain.change_case import ChangeCase, OwnerPlanSelection, PackMeaningSelection
from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import Pack
from eija_studio.domain.policy import apply_transaction, apply_transactions
from eija_studio.domain.transactions import Transaction


@dataclass(frozen=True)
class SemanticHistory:
    """Validated replay; models includes the selected meaning followed by each applied owner edit."""

    initial_count: int
    models: tuple[Workflow, ...]
    redo_models: tuple[Workflow, ...]


def _replay(model: Workflow, transactions: Sequence[Transaction], pack: Pack) -> tuple[Workflow, ...]:
    models = []
    for tx in transactions:
        model = apply_transaction(model, tx, pack)
        models.append(model)
    return tuple(models)


def _owner_plan_transactions(case: ChangeCase, selection: OwnerPlanSelection, pack: Pack) -> tuple[Transaction, ...]:
    """The immutable selected batch is bound to its original pack, baseline and selecting principal."""
    if (selection.pack_id != pack.id or selection.pack_digest != pack.digest
            or selection.baseline_semantic_hash != case.baseline.semantic_hash
            or case.selected_meaning is not None or not case.selected_by):
        raise DomainError("HISTORY_INCONSISTENT", "The selected owner plan no longer matches its pack and baseline")
    return tuple(step.transaction for step in selection.steps)


def _initial_transactions(case: ChangeCase, pack: Pack) -> tuple[Transaction, ...]:
    selection = case.selection
    if isinstance(selection, OwnerPlanSelection):
        return _owner_plan_transactions(case, selection, pack)
    if isinstance(selection, PackMeaningSelection) and selection.meaning != case.selected_meaning:
        raise DomainError("HISTORY_INCONSISTENT", "The tagged meaning disagrees with the stored meaning")
    meaning = pack.meaning(case.selected_meaning or "")
    if meaning is None or not meaning.supported:
        raise DomainError("HISTORY_INCONSISTENT", "The selected meaning cannot be replayed under this pack")
    return meaning.transactions


def replay(case: ChangeCase, pack: Pack) -> SemanticHistory:
    """Fail closed when stored commands no longer explain the candidate under the exact active pack."""
    candidate = case.executable()
    transactions = _initial_transactions(case, pack)
    count = len(transactions)
    if case.transactions[:count] != transactions:
        raise DomainError("HISTORY_INCONSISTENT", "The selection's atomic transaction prefix changed")
    try:
        initial = apply_transactions(case.baseline, transactions, pack)
        if isinstance(case.selection, OwnerPlanSelection) and initial.semantic_hash != case.selection.candidate_semantic_hash:
            raise DomainError("HISTORY_INCONSISTENT", "The selected owner plan does not reproduce its reviewed candidate")
        models = (initial, *_replay(initial, case.transactions[count:], pack))
        redo_models = _replay(candidate, tuple(reversed(case.redo_transactions)), pack)
    except (DomainError, ValidationError):
        raise DomainError("HISTORY_INCONSISTENT", "Stored semantic commands cannot be replayed safely") from None
    if models[-1] != candidate:
        raise DomainError("HISTORY_INCONSISTENT", "Stored semantic commands do not reproduce the current candidate")
    return SemanticHistory(count, models, redo_models)


def _entry(index: int, tx: Transaction, model: Workflow) -> dict[str, Any]:
    return {"index": index, "transaction": tx.model_dump(mode="json"),
            "model": model.model_dump(mode="json"), "semantic_hash": model.semantic_hash}


def _revisions(start: int, transactions: Iterable[Transaction], models: tuple[Workflow, ...]) -> list[dict[str, Any]]:
    return [_entry(i, tx, model) for i, (tx, model) in enumerate(zip(transactions, models, strict=True), start)]


def _selection(case: ChangeCase, pack: Pack, model: Workflow) -> dict[str, Any]:
    transactions = _initial_transactions(case, pack)
    owner_plan = isinstance(case.selection, OwnerPlanSelection)
    meaning = pack.meaning(case.selected_meaning or "")
    if not owner_plan and meaning is None:
        raise DomainError("HISTORY_INCONSISTENT", "The selected meaning is unavailable")
    return {"kind": "owner_plan" if owner_plan else "pack_meaning", "meaning": case.selected_meaning,
            "label": "Accepted owner plan" if owner_plan else meaning.label if meaning is not None else "",
            "selected_by": case.selected_by, "transaction_count": len(transactions),
            "transactions": [tx.model_dump(mode="json") for tx in transactions],
            "provenance": case.selection.model_dump(mode="json") if isinstance(case.selection, OwnerPlanSelection) else None,
            "model": model.model_dump(mode="json"), "semantic_hash": model.semantic_hash}


def _events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    kinds = {"SemanticEdited", "SemanticUndone", "SemanticRedone"}
    fields = ("by", "time", "from_version", "to_version", "transaction",
              "before_semantic_hash", "after_semantic_hash", "discarded_redo")
    return [{"seq": event["seq"], "kind": event["kind"],
             "body": {key: event["body"][key] for key in fields if key in event["body"]}}
            for event in events if event["kind"] in kinds]


def history_view(case: ChangeCase, pack: Pack, events: list[dict[str, Any]]) -> dict[str, Any]:
    """Read-only models for navigation plus actual command audit entries; no invented legacy timestamps."""
    result: dict[str, Any] = {
        "case_id": case.id, "version": case.version, "stage": case.stage, "scope": "semantic",
        "status": "meaning_required", "can_undo": False, "can_redo": False, "cursor": 0,
        "selection": None, "edits": [], "redo": [], "events": _events(events),
        "audit_note": "Models are reconstructed semantic revisions, not case or evidence snapshots. "
                      "Command timestamps exist only for edits recorded with semantic history. "
                      "Layout is excluded; receipts and decisions are never restored by undo.",
    }
    if case.selected_meaning is None and case.candidate is None:
        if case.transactions or case.redo_transactions:
            raise DomainError("HISTORY_INCONSISTENT", "Semantic commands exist without a selected meaning")
        return result
    history = replay(case, pack)
    edits = case.transactions[history.initial_count:]
    editable = case.stage not in {"APPLIED", "DISCARDED"}
    result.update({
        "status": "ready", "cursor": len(edits),
        "can_undo": editable and bool(edits), "can_redo": editable and bool(case.redo_transactions),
        "selection": _selection(case, pack, history.models[0]),
        "edits": _revisions(1, edits, history.models[1:]),
        "redo": _revisions(len(edits) + 1, reversed(case.redo_transactions), history.redo_models),
    })
    return result


def command_event(case: ChangeCase, model: Workflow, tx: Transaction, by: str, time: str,
                  discarded_redo: Sequence[Transaction] = ()) -> dict[str, Any]:
    """Append-only command provenance; decision and receipt payloads remain in their existing audit."""
    return {"case_id": case.id, "by": by, "time": time, "from_version": case.version,
            "to_version": case.version + 1, "transaction": tx.model_dump(mode="json"),
            "before_semantic_hash": case.executable().semantic_hash, "after_semantic_hash": model.semantic_hash,
            "discarded_redo": [item.model_dump(mode="json") for item in reversed(discarded_redo)]}
