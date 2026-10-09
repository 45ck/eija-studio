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

from eija_studio.application.new_system import FIELD as FIELD_NAME
from eija_studio.application.new_system import classes
from eija_studio.application.new_system import NAME as IDENTIFIER
from eija_studio.domain.laws import reachable
from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import Pack
from .providers.offline import matches_rule

SPLIT = re.compile(r"\s*(?:;|\n|,?\s+then\s+|,?\s+and then\s+)\s*", re.IGNORECASE)
NAME = r"([A-Za-z][\w-]*)"
HELP = ("Use one change per clause, with exact model names, joined by 'then': add state <S> [after <T>]; rename state <A> "
        "to <B>; remove state <S>; start in <S>; add <action> from <A> to <B> for <role>; remove <action>; allow <role> "
        "to <action>; move <action> source|target to <S>. On a system you started, also: add field <name> [as "
        "text|number|date|boolean|choice <A>, <B>] [required]; remove field <name>; make <field> required|optional. "
        "Or describe a change the pack models.")
TYPES = {"text": "text", "number": "number", "date": "date", "boolean": "boolean", "yes/no": "boolean", "choice": "choice"}
FIELD = r"(?:field|attribute)"


def _transition_id(model: Workflow, action: str) -> str:
    taken, base = {t.id for t in model.transitions}, "TR-" + re.sub(r"[^A-Z0-9]+", "_", action.upper()).strip("_")
    return next(f"{base}{n or ''}" for n in range(len(taken) + 2) if f"{base}{n or ''}" not in taken)


def _normalise(text: str) -> str:
    return " ".join(text.strip().rstrip(".!").split())


Classes = tuple[str, dict[str, list[str]]]  # the record class, and each class's attribute names
Step = dict[str, Any] | list[dict[str, Any]]  # one clause reads as one step, or as the few steps it needs (grows only)


def _from_clauses(steps: list[Step], clauses: list[str]) -> dict[str, Any]:
    planned = [(tx, c) for s, c in zip(steps, clauses, strict=True) for tx in (s if isinstance(s, list) else [s])]
    return {"summary": f"{len(planned)} step{'' if len(planned) == 1 else 's'} from your request", "meaning": None,
            "steps": [{"transaction": tx, "why": f"You asked: “{c}”"} for tx, c in planned]}


class _Clause:
    """Resolves one clause against the model and pack, or returns None when it is not one of the phrases."""

    def __init__(self, model: Workflow, pack: Pack, grows: bool = False):
        self.model, self.pack, self.grows = model, pack, grows
        self.planned: list[str] = []  # states added or renamed by earlier clauses of the same plan
        self.named: list[str] = []  # actions and roles this plan names that the pack does not declare (grows only)
        self.removed: set[str] = set()  # transitions an earlier clause of this plan removes
        self.fields: list[str] = []  # attributes added by earlier clauses of the same plan (grows only)
        self.patterns: list[tuple[re.Pattern[str], Callable[..., Step]]] = [
            (re.compile(rf"^add state {NAME}(?: after {NAME})?$", re.I), self._add_state),
            (re.compile(rf"^rename (?:state )?{NAME} to {NAME}$", re.I), self._rename),
            (re.compile(rf"^(?:remove|delete) state {NAME}$", re.I), self._remove_state),
            (re.compile(rf"^(?:start (?:records )?in|make) {NAME}(?: the initial state)?$", re.I), self._initial),
            (re.compile(rf"^add (?:transition )?{NAME} from {NAME} to {NAME} for {NAME}$", re.I), self._add_transition),
            (re.compile(rf"^(?:remove|delete) (?:transition )?{NAME}$", re.I), self._remove_transition),
            (re.compile(rf"^(?:allow|let) {NAME} (?:to )?{NAME}$", re.I), self._role),
            (re.compile(rf"^move {NAME} (source|target) to {NAME}$", re.I), self._retarget),
            (re.compile(rf"^add (required |optional )?{FIELD} {NAME}(?: to {NAME})?(?:(?: as|:| :) (?:an? )?"
                        rf"(text|number|date|boolean|yes/no|choice)(?:(?: of| from|:)? (.+?))?)?( required| optional)?$", re.I), self._add_field),
            (re.compile(rf"^(?:remove|delete) {FIELD} {NAME}(?: from {NAME})?$", re.I), self._remove_field),
            (re.compile(rf"^make (?:{FIELD} )?{NAME} (required|optional)$", re.I), self._require),
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
            if self.grows:
                return self._new_name("role", name)
            raise DomainError("PLAN_UNKNOWN_NAME", f"The pack has no role {name}")
        return found

    def _new_name(self, kind: str, name: str) -> str:
        """A name this system does not have yet, spelled as an earlier clause of the same plan spelled it."""
        earlier = next((n for n in self.named if n.casefold() == name.casefold()), None)
        if earlier is not None:
            return earlier
        if not re.fullmatch(IDENTIFIER, name):
            raise DomainError("PLAN_UNKNOWN_NAME", f"A new {kind} is named with letters, digits and _ (not {name})")
        self.named.append(name)
        return name

    def _add_state(self, state: str, after: str | None) -> dict[str, Any]:
        self.planned.append(state)
        return {"kind": "add_state", "state": state, "after": self.state(after) if after else None}

    def known(self, name: str) -> bool:
        return any(s.casefold() == name.casefold() for s in (*self.model.states, *self.planned))

    def _rename(self, state: str, to: str) -> dict[str, Any]:
        self.planned.append(to)
        return {"kind": "rename_state", "state": self.state(state), "to": to}

    def _remove_state(self, state: str) -> dict[str, Any] | list[dict[str, Any]]:
        found = self.state(state)
        step = {"kind": "remove_state", "state": found}
        using = [t.id for t in self.model.transitions if found in (t.from_state, t.to_state) and t.id not in self.removed]
        if not self.grows or not using:
            return step
        self.removed.update(using)
        return [*({"kind": "remove_transition", "transition": t} for t in using), step]

    def _initial(self, state: str) -> dict[str, Any]:
        return {"kind": "set_initial", "state": self.state(state)}

    def _add_transition(self, action: str, source: str, target: str, role: str) -> Step:
        declared = next((a.id for a in self.pack.actions if a.id.casefold() == action.casefold()), None)
        if declared is None and not self.grows:
            raise DomainError("PLAN_UNKNOWN_NAME", f"The pack declares no action {action}; its actions are {', '.join(a.id for a in self.pack.actions)}")
        declared = declared or self._new_name("action", action)
        before = self._new_states(source, target)
        step = {"kind": "add_transition", "id": _transition_id(self.model, declared), "action": declared, "from_state": self._state_or_new(source),
                "to_state": self._state_or_new(target), "role": self.role(role)}
        return [*before, step] if before else step

    def _new_states(self, *names: str) -> list[dict[str, Any]]:
        """On a system that grows, a step adding each state a transition names that nothing has yet, first."""
        if not self.grows:
            return []
        steps = []
        for state in dict.fromkeys(n for n in names if not self.known(n)):
            if not re.fullmatch(IDENTIFIER, state):
                raise DomainError("PLAN_UNKNOWN_NAME", f"A new state is named with letters, digits and _ (not {state})")
            steps.append(self._add_state(state, None))
        return steps

    def _state_or_new(self, name: str) -> str:
        """A state added earlier in the same plan is not in the model yet; the application checks it exists by then."""
        return next((s for s in (*self.model.states, *self.planned) if s.casefold() == name.casefold()), name)

    def _remove_transition(self, name: str) -> dict[str, Any]:
        found = self.transition(name)
        self.removed.add(found)
        return {"kind": "remove_transition", "transition": found}

    def _role(self, role: str, name: str) -> dict[str, Any]:
        return {"kind": "set_role", "transition": self.transition(name), "role": self.role(role)}

    def _retarget(self, name: str, end: str, state: str) -> dict[str, Any]:
        return {"kind": "retarget_transition", "transition": self.transition(name), "end": end.lower(), "state": self._state_or_new(state)}

    def _data(self) -> Classes:
        """The class diagram a data-model phrase changes: only on a system you started (ADR-0202)."""
        if not self.grows:
            raise DomainError("PLAN_DATA_FIXED", "This system's class diagram is its owner's; chat adds fields only on a system you started")
        data = classes(self.pack)
        if data is None:
            raise DomainError("PLAN_UNKNOWN_NAME", "This system has no class diagram to add a field to")
        return data

    def _class(self, data: Classes, name: str | None) -> str:
        if name is None:
            return data[0]
        found = next((e for e in data[1] if e.casefold() == name.casefold()), None)
        if found is None:
            raise DomainError("PLAN_UNKNOWN_NAME", f"The class diagram has no class {name}")
        return found

    def _field(self, data: Classes, entity: str, name: str) -> str:
        names = data[1][entity] + self.fields
        found = next((n for n in names if n.casefold() == name.casefold()), None)
        if found is None:
            raise DomainError("PLAN_UNKNOWN_NAME", f"{entity} has no field {name}")
        return found

    def _add_field(self, first: str | None, name: str, entity: str | None, kind: str | None, options: str | None,
                   last: str | None) -> dict[str, Any]:
        data = self._data()
        field = name[:1].lower() + name[1:]
        if not re.fullmatch(FIELD_NAME, field):
            raise DomainError("PLAN_UNKNOWN_NAME", f"A field is named with letters, digits and _ (not {name})")
        type_ = TYPES[(kind or "text").lower()]
        choices = [c.strip() for c in re.split(r",|\bor\b", options or "") if c.strip()]
        if (type_ == "choice") != bool(choices):
            raise DomainError("PLAN_UNKNOWN_NAME", "A choice field lists its choices, for example: as choice Small, Medium, Large")
        self.fields.append(field)
        required = "required" in f"{first or ''} {last or ''}".lower()
        attribute = {"name": field, "type": type_, "required": required} | ({"choices": choices} if choices else {})
        return {"kind": "add_attribute", "entity": self._class(data, entity), "attribute": attribute}

    def _remove_field(self, name: str, entity: str | None) -> dict[str, Any]:
        data = self._data()
        found = self._class(data, entity)
        return {"kind": "remove_attribute", "entity": found, "name": self._field(data, found, name)}

    def _require(self, name: str, how: str) -> dict[str, Any]:
        data = self._data()
        return {"kind": "set_required", "entity": data[0], "name": self._field(data, data[0], name),
                "required": how.lower() == "required"}

    def resolve(self, clause: str) -> Step | None:
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


def _first_unread(clauses: list[str], steps: list[Step | None]) -> str:
    return next(c for c, step in zip(clauses, steps, strict=True) if step is None)


class OfflinePlanProposer:
    name, live = "offline-plan-fixture-v1", False

    def propose(self, request: str, model: Workflow, pack: Pack, *, grows: bool = False) -> dict[str, Any]:
        clauses = [_normalise(c) for c in SPLIT.split(request) if _normalise(c)]
        if not clauses:
            raise DomainError("PLAN_REQUEST_UNSUPPORTED", HELP)
        resolver = _Clause(model, pack, grows)
        steps = [resolver.resolve(c) for c in clauses]
        read = [s for s in steps if s]
        if len(read) == len(steps):
            return _from_clauses(read, clauses)
        planned = _meaning_plan(request, pack) if not any(steps) else None  # never drop clauses that were read
        if planned is None:
            raise DomainError("PLAN_REQUEST_UNSUPPORTED", f"I could not read “{_first_unread(clauses, steps)}”. {HELP}")
        return planned

    def follow_on(self, ripple: dict[str, Any], model: Workflow, pack: Pack) -> dict[str, Any]:
        return follow_ons(ripple, model, pack)


def _spare_action(model: Workflow, pack: Pack) -> str | None:
    """A declared action the model does not use yet. Each action labels one transition, so there is no other choice:
    when every declared action is in use, no follow-on is proposed rather than one the policy is sure to refuse."""
    used = {t.action for t in model.transitions}
    return next((a.id for a in pack.actions if a.id not in used), None)


def _role_for(model: Workflow, pack: Pack, action: str) -> str:
    """The role that already takes `action`, else the role that takes the most transitions."""
    takes = [t.role for t in model.transitions if t.action == action] or [t.role for t in model.transitions]
    return max(sorted(set(takes)), key=takes.count) if takes else pack.roles[0].id


def _transition(model: Workflow, pack: Pack, source: str, target: str) -> dict[str, Any] | None:
    action = _spare_action(model, pack)
    if action is None:
        return None
    return {"kind": "add_transition", "id": _transition_id(model, action), "action": action, "from_state": source,
            "to_state": target, "role": _role_for(model, pack, action)}


def _into(model: Workflow, pack: Pack, state: str) -> dict[str, Any] | None:
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
        step = _into(model, pack, name)
        return {"transaction": step, "why": f"So records can reach {name}"} if step else None
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
