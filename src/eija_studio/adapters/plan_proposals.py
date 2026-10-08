"""Offline plan proposer for the PlayIDE chat (ADR-0156): a bounded phrase grammar and the pack's modelled meanings,
never an LLM. Its plans are untrusted proposals like any other; the application re-checks every step.

A request is split into clauses ("then", ";", new lines). Each clause must be one complete phrase using exact model
names, for example "add state Archived after <state>" or "add <action> from <state> to Archived for <role>". A request
none of whose clauses match a phrase is matched against the pack's proposal rules, and a supported meaning with transactions
becomes the plan. Anything else is refused with the phrases it understands.
"""
from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import Pack

SPLIT = re.compile(r"\s*(?:;|\n|,?\s+then\s+|,?\s+and then\s+)\s*", re.IGNORECASE)
NAME = r"([A-Za-z][\w-]*)"
HELP = ("Use one change per clause, with exact model names, joined by 'then': add state <S> [after <T>]; rename state <A> "
        "to <B>; remove state <S>; start in <S>; add <action> from <A> to <B> for <role>; remove <action>; allow <role> "
        "to <action>; move <action> source|target to <S>. Or describe a change the pack models.")


def _normalise(text: str) -> str:
    return " ".join(text.strip().rstrip(".!").split())


class _Clause:
    """Resolves one clause against the model and pack, or returns None when it is not one of the phrases."""

    def __init__(self, model: Workflow, pack: Pack):
        self.model, self.pack = model, pack
        self.planned: list[str] = []  # states added or renamed by earlier clauses of the same plan
        self.patterns: list[tuple[re.Pattern[str], Callable[..., dict[str, Any]]]] = [
            (re.compile(rf"^add state {NAME}(?: after {NAME})?$", re.I), self._add_state),
            (re.compile(rf"^rename (?:state )?{NAME} to {NAME}$", re.I), self._rename),
            (re.compile(rf"^(?:remove|delete) state {NAME}$", re.I), self._remove_state),
            (re.compile(rf"^(?:start (?:records )?in|make) {NAME}(?: the initial state)?$", re.I), self._initial),
            (re.compile(rf"^add (?:transition )?{NAME} from {NAME} to {NAME} for {NAME}$", re.I), self._add_transition),
            (re.compile(rf"^(?:remove|delete) (?:transition )?{NAME}$", re.I), self._remove_transition),
            (re.compile(rf"^(?:allow|let) {NAME} (?:to )?{NAME}$", re.I), self._role),
            (re.compile(rf"^move {NAME} (source|target) to {NAME}$", re.I), self._retarget),
        ]

    def state(self, name: str) -> str:
        found = next((s for s in (*self.model.states, *self.planned) if s.casefold() == name.casefold()), None)
        if found is None:
            raise DomainError("PLAN_UNKNOWN_NAME", f"The model has no state {name}")
        return found

    def transition(self, name: str) -> str:
        found = [t.id for t in self.model.transitions if name.casefold() in (t.id.casefold(), t.action.casefold())]
        if len(found) != 1:
            raise DomainError("PLAN_UNKNOWN_NAME", f"The model has no single transition or action {name}")
        return found[0]

    def role(self, name: str) -> str:
        found = next((r.id for r in self.pack.roles if r.id.casefold() == name.casefold()), None)
        if found is None:
            raise DomainError("PLAN_UNKNOWN_NAME", f"The pack has no role {name}")
        return found

    def _add_state(self, state: str, after: str | None) -> dict[str, Any]:
        self.planned.append(state)
        return {"kind": "add_state", "state": state, "after": self.state(after) if after else None}

    def _rename(self, state: str, to: str) -> dict[str, Any]:
        self.planned.append(to)
        return {"kind": "rename_state", "state": self.state(state), "to": to}

    def _remove_state(self, state: str) -> dict[str, Any]:
        return {"kind": "remove_state", "state": self.state(state)}

    def _initial(self, state: str) -> dict[str, Any]:
        return {"kind": "set_initial", "state": self.state(state)}

    def _add_transition(self, action: str, source: str, target: str, role: str) -> dict[str, Any]:
        declared = next((a.id for a in self.pack.actions if a.id.casefold() == action.casefold()), None)
        if declared is None:
            raise DomainError("PLAN_UNKNOWN_NAME", f"The pack declares no action {action}; its actions are {', '.join(a.id for a in self.pack.actions)}")
        taken, base = {t.id for t in self.model.transitions}, "TR-" + re.sub(r"[^A-Z0-9]+", "_", declared.upper()).strip("_")
        tid = next(f"{base}{n or ''}" for n in range(len(taken) + 2) if f"{base}{n or ''}" not in taken)
        return {"kind": "add_transition", "id": tid, "action": declared, "from_state": self._state_or_new(source),
                "to_state": self._state_or_new(target), "role": self.role(role)}

    def _state_or_new(self, name: str) -> str:
        """A state added earlier in the same plan is not in the model yet; the application checks it exists by then."""
        return next((s for s in self.model.states if s.casefold() == name.casefold()), name)

    def _remove_transition(self, name: str) -> dict[str, Any]:
        return {"kind": "remove_transition", "transition": self.transition(name)}

    def _role(self, role: str, name: str) -> dict[str, Any]:
        return {"kind": "set_role", "transition": self.transition(name), "role": self.role(role)}

    def _retarget(self, name: str, end: str, state: str) -> dict[str, Any]:
        return {"kind": "retarget_transition", "transition": self.transition(name), "end": end.lower(), "state": self._state_or_new(state)}

    def resolve(self, clause: str) -> dict[str, Any] | None:
        for pattern, build in self.patterns:
            match = pattern.match(clause)
            if match:
                return build(*match.groups())
        return None


def _meaning_plan(request: str, pack: Pack) -> dict[str, Any] | None:
    """The first supported meaning with transactions among the pack's proposal rules that match the request."""
    words = set(re.findall(r"[a-z]+", request.casefold()))
    for rule in pack.fixtures.proposals.rules:
        if set(rule.all) <= words and (not rule.any or words & set(rule.any)):
            for alternative in rule.alternatives:
                meaning = pack.meaning(alternative.interpretation)
                if meaning is not None and meaning.supported and meaning.transactions:
                    return {"summary": meaning.label, "meaning": meaning.id,
                            "steps": [{"transaction": t.model_dump(mode="json"), "why": alternative.explanation} for t in meaning.transactions]}
    return None


def _first_unread(clauses: list[str], steps: list[dict[str, Any] | None]) -> str:
    return next(c for c, step in zip(clauses, steps, strict=True) if step is None)


class OfflinePlanProposer:
    name, live = "offline-plan-fixture-v1", False

    def propose(self, request: str, model: Workflow, pack: Pack) -> dict[str, Any]:
        clauses = [_normalise(c) for c in SPLIT.split(request) if _normalise(c)]
        if not clauses:
            raise DomainError("PLAN_REQUEST_UNSUPPORTED", HELP)
        resolver = _Clause(model, pack)
        steps = [resolver.resolve(c) for c in clauses]
        if all(steps):
            return {"summary": f"{len(steps)} step(s) from your request", "meaning": None,
                    "steps": [{"transaction": s, "why": f"You asked: “{c}”"} for s, c in zip(steps, clauses, strict=True)]}
        planned = _meaning_plan(request, pack) if not any(steps) else None  # never drop clauses that were read
        if planned is None:
            raise DomainError("PLAN_REQUEST_UNSUPPORTED", f"I could not read “{_first_unread(clauses, steps)}”. {HELP}")
        return planned
