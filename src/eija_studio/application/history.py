"""Semantic history is a projection of typed commands, replayed by the existing policy interpreter.

The selected meaning is one protected atomic batch. Owner edits and undone edits are individual
commands. These reconstructed models are not historical verification receipts or case snapshots.
"""
from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from eija_studio.domain.change_case import ChangeCase
from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import Meaning, Pack
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


def replay(case: ChangeCase, pack: Pack) -> SemanticHistory:
    """Fail closed when stored commands no longer explain the candidate under the exact active pack."""
    candidate = case.executable()
    meaning = pack.meaning(case.selected_meaning or "")
    if meaning is None or not meaning.supported:
        raise DomainError("HISTORY_INCONSISTENT", "The selected meaning cannot be replayed under this pack")
    count = len(meaning.transactions)
    if case.transactions[:count] != meaning.transactions:
        raise DomainError("HISTORY_INCONSISTENT", "The selected meaning's atomic transaction prefix changed")
    try:
        initial = apply_transactions(case.baseline, meaning.transactions, pack)
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


def _selection(case: ChangeCase, meaning: Meaning, model: Workflow) -> dict[str, Any]:
    return {"meaning": meaning.id, "label": meaning.label, "selected_by": case.selected_by,
            "transaction_count": len(meaning.transactions),
            "transactions": [tx.model_dump(mode="json") for tx in meaning.transactions],
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
    meaning = pack.meaning(case.selected_meaning or "")
    # replay has already checked that the exact supported meaning exists.
    if meaning is None:
        raise DomainError("HISTORY_INCONSISTENT", "The selected meaning is unavailable")
    edits = case.transactions[history.initial_count:]
    editable = case.stage not in {"APPLIED", "DISCARDED"}
    result.update({
        "status": "ready", "cursor": len(edits),
        "can_undo": editable and bool(edits), "can_redo": editable and bool(case.redo_transactions),
        "selection": _selection(case, meaning, history.models[0]),
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
