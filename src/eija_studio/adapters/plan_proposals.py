"""Offline plan proposer for the PlayIDE chat (ADR-0156): a bounded phrase grammar and the pack's modelled meanings,
never an LLM. Its plans are untrusted proposals like any other; the application re-checks every step.

It also proposes follow-on edits for a ripple (ADR-0158) by fixed rules: the default screen for a new use case, no screen for a
removed one, and a transition into a state nothing reaches or out of a state left with no way out, using a declared
action the model does not use yet. These are guesses for the person to accept or reject, re-checked like any step.

A request is split into clauses ("then", ";", new lines). Each clause must be one complete phrase using exact model
names, for example "add state Archived after <state>" or "add <action> from <state> to Archived for <role>". A request
none of whose clauses match a phrase is matched against the pack's proposal rules, and a supported meaning with transactions
becomes the plan. Anything else is refused with the phrases it understands.
"""
from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

from eija_studio.domain.laws import reachable
from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import Pack
from .providers.offline import matches_rule

SPLIT = re.compile(r"\s*(?:;|\n|,?\s+then\s+|,?\s+and then\s+)\s*", re.IGNORECASE)
NAME = r"([A-Za-z][\w-]*)"
HELP = ("Use one change per clause, with exact model names, joined by 'then': add state <S> [after <T>]; rename state <A> "
        "to <B>; remove state <S>; start in <S>; add <action> from <A> to <B> for <role>; remove <action>; allow <role> "
        "to <action>; move <action> source|target to <S>. Or describe a change the pack models.")


def _transition_id(model: Workflow, action: str) -> str:
    taken, base = {t.id for t in model.transitions}, "TR-" + re.sub(r"[^A-Z0-9]+", "_", action.upper()).strip("_")
    return next(f"{base}{n or ''}" for n in range(len(taken) + 2) if f"{base}{n or ''}" not in taken)


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
        return {"kind": "add_transition", "id": _transition_id(self.model, declared), "action": declared, "from_state": self._state_or_new(source),
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
    for rule in pack.fixtures.proposals.rules:
        if matches_rule(rule, request):
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

    def follow_on(self, ripple: dict[str, Any], model: Workflow, pack: Pack) -> dict[str, Any]:
        return follow_ons(ripple, model, pack)


def _spare_action(model: Workflow, pack: Pack, source: str) -> str:
    """A declared action the model does not use yet, else one already leaving `source`, else the first declared."""
    used = {t.action for t in model.transitions}
    spare = [a.id for a in pack.actions if a.id not in used]
    leaving = [t.action for t in model.transitions if t.from_state == source]
    return (spare or leaving or [pack.actions[0].id])[0]


def _role_for(model: Workflow, pack: Pack, action: str) -> str:
    """The role that already takes `action`, else the role that takes the most transitions."""
    takes = [t.role for t in model.transitions if t.action == action] or [t.role for t in model.transitions]
    return max(sorted(set(takes)), key=takes.count) if takes else pack.roles[0].id


def _transition(model: Workflow, pack: Pack, source: str, target: str) -> dict[str, Any]:
    action = _spare_action(model, pack, source)
    return {"kind": "add_transition", "id": _transition_id(model, action), "action": action, "from_state": source,
            "to_state": target, "role": _role_for(model, pack, action)}


def _into(model: Workflow, pack: Pack, state: str) -> dict[str, Any]:
    """A transition into `state` from the nearest reachable state before it that records can already leave."""
    edges = [(t.from_state, t.to_state) for t in model.transitions]
    live = [s for s in model.states if s in reachable(edges, model.initial_state) and s in {a for a, _ in edges}]
    before = [s for s in live if model.states.index(s) < model.states.index(state)]
    return _transition(model, pack, (before or live or [model.initial_state])[-1], state)


def _ends(model: Workflow, state: str) -> list[str]:
    """End states (no way out) other than `state`: first those its neighbours (the states that lead into it) also
    lead to, else every end state, once per transition into it."""
    exits = {t.from_state for t in model.transitions}
    ends = [t.to_state for t in model.transitions if t.to_state != state and t.to_state not in exits]
    return _near(model, state, set(ends)) or ends


def _near(model: Workflow, state: str, ends: set[str]) -> list[str]:
    """The end states that the states leading into `state` also lead to."""
    neighbours = {t.from_state for t in model.transitions if t.to_state == state}
    return [t.to_state for t in model.transitions if t.from_state in neighbours and t.to_state in ends]


def _out_of(model: Workflow, pack: Pack, state: str) -> dict[str, Any] | None:
    """A transition from `state` to the end state `_ends` names most often."""
    ends = _ends(model, state)
    return _transition(model, pack, state, max(sorted(set(ends)), key=ends.count)) if ends else None


def _state_follow_on(code: str, model: Workflow, pack: Pack, name: str) -> dict[str, Any] | None:
    if code == "STATE_UNREACHABLE":
        return {"transaction": _into(model, pack, name), "why": f"So records can reach {name}"}
    step = _out_of(model, pack, name) if code == "STATE_NO_EXIT" else None
    return {"transaction": step, "why": f"So records in {name} can move on"} if step else None


def _screen_follow_on(code: str, name: str) -> dict[str, Any] | None:
    case = None if name == "None" else name
    if code == "SCREEN_UNKNOWN_USE_CASE":
        return {"screen": {"op": "remove", "use_case": case}, "why": f"{case} is no longer a use case, so its screen cannot be built"}
    if code in ("SCREEN_MISSING_USE_CASE", "SCREEN_MISSING_CREATE"):
        return {"screen": {"op": "add", "use_case": case}, "why": f"Every use case needs a screen; this is the default for {case or 'creating a record'}"}
    return None


def _follow_on(problem: dict[str, Any], model: Workflow, pack: Pack) -> dict[str, Any] | None:
    kind, _, name = str(problem.get("ref") or "").partition(":")
    code = str(problem.get("code"))
    if kind == "state":
        return _state_follow_on(code, model, pack, name)
    return _screen_follow_on(code, name) if kind == "screen" else None


def follow_ons(ripple: dict[str, Any], model: Workflow, pack: Pack) -> dict[str, Any]:
    """One follow-on step per ripple problem it has a rule for, each naming the problem it is meant to fix."""
    steps = []
    for problem in ripple.get("problems", []):
        step = _follow_on(problem, model, pack)
        if step is not None:
            steps.append(step | {"fixes": problem.get("code")})
    return {"steps": steps}
