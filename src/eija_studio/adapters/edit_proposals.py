"""Bounded offline request fixture: exact model names and complete phrases, never an LLM."""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any, Literal

from eija_studio.domain.models import DomainError, Transition, Workflow
from eija_studio.domain.transactions import RetargetTransition, SetRole, Transaction


def _normalise(text: str) -> str:
    return " ".join(text.strip().removesuffix(".").split()).casefold()


def _role_requests(transition: Transition, role: str) -> Iterator[tuple[str, Transaction]]:
    transaction = SetRole(kind="set_role", transition=transition.id, role=role)
    for name in (transition.action, transition.id):
        yield f"Allow {role} to {name}", transaction
        yield f"Set {name} role to {role}", transaction


def _endpoint_requests(transition: Transition, state: str) -> Iterator[tuple[str, Transaction]]:
    ends: tuple[Literal["source", "target"], ...] = ("source", "target")
    for end in ends:
        transaction = RetargetTransition(kind="retarget_transition", transition=transition.id, end=end, state=state)
        for name in (transition.action, transition.id):
            yield f"Move {name} {end} to {state}", transaction


def _requests(model: Workflow, choices: tuple[Transaction, ...]) -> Iterator[tuple[str, Transaction]]:
    roles = {transition.role for transition in model.transitions}
    roles.update(choice.role for choice in choices if isinstance(choice, SetRole))
    for transition in model.transitions:
        for role in sorted(roles):
            yield from _role_requests(transition, role)
        for state in model.states:
            yield from _endpoint_requests(transition, state)


class OfflineEditProposer:
    """Resolve one complete request against captured choices, including refused choices and current values."""

    def propose(self, request: str, model: Workflow, choices: tuple[Transaction, ...]) -> dict[str, Any]:
        text = _normalise(request)
        matches = {transaction for phrase, transaction in _requests(model, choices) if _normalise(phrase) == text}
        if not matches:
            raise DomainError("EDIT_REQUEST_UNSUPPORTED", "Use one complete request: Move <action> source or target to <state>, or Allow <role> to <action>. Use exact model names.")
        if len(matches) != 1:
            raise DomainError("EDIT_REQUEST_AMBIGUOUS", "This request matches more than one model identity; use an exact transition ID.")
        transaction = matches.pop()
        if transaction not in choices:
            raise DomainError("EDIT_REQUEST_NO_CHANGE", "This request already describes the current model; no edit was proposed.")
        return transaction.model_dump(mode="json")
