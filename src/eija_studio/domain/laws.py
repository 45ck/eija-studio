"""Typed law DSL of a domain pack: what a workflow may never do, stated as data (WBS 1.1/1.2).

A law is a small typed record (a discriminated union on ``kind``); its ``code`` is the error code the policy
reports when the law is violated, and its ``id`` is the stable reference a refusal points at (``law:<id>``).
``evaluate_table`` judges a workflow's transition table; ``evaluate_run`` judges one executed run (a sequence
of steps), which is where sequence laws such as ``path_requires`` bite at runtime.

Nothing here names a domain: every state, role, action and effect comes from the pack.
"""
from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from typing import Annotated, Any, Literal, Union

from pydantic import Field

from .models import Contract, Guard, Transition, Workflow

LAW_ID = r"^[a-z][a-z0-9-]{0,63}$"
CODE = r"^[A-Z][A-Z0-9_]{0,63}(:[A-Za-z0-9_-]{1,64})?$"
Name = Annotated[str, Field(min_length=1, max_length=60)]


class When(Contract):
    """Condition under which a law applies. Both unset means always."""
    action_present: Name | None = None
    action_absent: Name | None = None


class _Law(Contract):
    id: str = Field(pattern=LAW_ID)
    code: str = Field(pattern=CODE)
    description: str = Field(default="", max_length=400)
    when: When | None = None


class ClosedShape(_Law):
    """The workflow has exactly these states and actions and this initial state."""
    kind: Literal["closed_shape"]
    states: tuple[Name, ...] = Field(min_length=1)
    actions: tuple[Name, ...] = Field(min_length=1)
    initial_state: Name


class OnlyRoleHolds(_Law):
    """Every transition performing ``action`` is held by ``role``."""
    kind: Literal["only_role_holds"]
    action: Name
    role: Name


class RoleNeverHolds(_Law):
    """No transition performing ``action`` is held by ``role``."""
    kind: Literal["role_never_holds"]
    action: Name
    role: Name


class RoleNeverEnters(_Law):
    """No transition held by ``role`` enters ``state``."""
    kind: Literal["role_never_enters"]
    role: Name
    state: Name


class StateOnlyVia(_Law):
    """Every transition entering ``state`` performs one of ``actions``."""
    kind: Literal["state_only_via"]
    state: Name
    actions: tuple[Name, ...] = Field(min_length=1)


class ActionTarget(_Law):
    """Every transition performing ``action`` ends in ``state``."""
    kind: Literal["action_target"]
    action: Name
    state: Name


class ActionSourceIn(_Law):
    """Every transition performing ``action`` starts in one of ``states``."""
    kind: Literal["action_source_in"]
    action: Name
    states: tuple[Name, ...] = Field(min_length=1)


class ActionRequiresGuard(_Law):
    """Every transition performing ``action`` carries at least ``guards``."""
    kind: Literal["action_requires_guard"]
    action: Name
    guards: tuple[Guard, ...] = Field(min_length=1)


class ForbiddenEffects(_Law):
    """No transition requires any of ``effects`` and every transition declares them forbidden."""
    kind: Literal["forbidden_effects"]
    effects: tuple[Name, ...] = Field(min_length=1)


class StateFinal(_Law):
    """No transition leaves ``state``."""
    kind: Literal["state_final"]
    state: Name


class PathRequires(_Law):
    """Every path from the initial state to ``state`` passes through ``via`` (a sequence law)."""
    kind: Literal["path_requires"]
    state: Name
    via: Name


class RequiresEvidence(_Law):
    """A review needs evidence of this kind; judged by the evidence matrix, never by the table."""
    kind: Literal["requires_evidence"]
    evidence: str = Field(pattern=r"^[a-z][a-z0-9_]{0,39}$")


Law = Annotated[Union[ClosedShape, OnlyRoleHolds, RoleNeverHolds, RoleNeverEnters, StateOnlyVia, ActionTarget,  # noqa: UP007
                      ActionSourceIn, ActionRequiresGuard, ForbiddenEffects, StateFinal, PathRequires, RequiresEvidence],
                Field(discriminator="kind")]
LAW_KINDS = ("closed_shape", "only_role_holds", "role_never_holds", "role_never_enters", "state_only_via", "action_target",
             "action_source_in", "action_requires_guard", "forbidden_effects", "state_final", "path_requires", "requires_evidence")


@dataclass(frozen=True)
class Violation:
    """One broken law: its id, the code the policy reports, and the model elements involved."""
    law: str
    code: str
    refs: tuple[str, ...]


@dataclass(frozen=True)
class Step:
    """One executed transition of a run."""
    action: str
    role: str
    source: str
    target: str
    effects: tuple[str, ...] = ()


def applies(law: _Law, actions: set[str]) -> bool:
    if law.when is None:
        return True
    present = law.when.action_present is None or law.when.action_present in actions
    absent = law.when.action_absent is None or law.when.action_absent not in actions
    return present and absent


# ---- per-transition predicates: True means the transition breaks the law ----------------------------------

def _breaks(law: _Law, t: Transition) -> bool:
    check = _TRANSITION_CHECKS.get(type(law))
    return check is not None and check(law, t)


def _only_role(law: OnlyRoleHolds, t: Transition) -> bool:
    return t.action == law.action and t.role != law.role


def _never_role(law: RoleNeverHolds, t: Transition) -> bool:
    return t.action == law.action and t.role == law.role


def _never_enters(law: RoleNeverEnters, t: Transition) -> bool:
    return t.role == law.role and t.to_state == law.state


def _only_via(law: StateOnlyVia, t: Transition) -> bool:
    return t.to_state == law.state and t.action not in law.actions


def _target(law: ActionTarget, t: Transition) -> bool:
    return t.action == law.action and t.to_state != law.state


def _source(law: ActionSourceIn, t: Transition) -> bool:
    return t.action == law.action and t.from_state not in law.states


def _guard(law: ActionRequiresGuard, t: Transition) -> bool:
    return t.action == law.action and not set(law.guards) <= set(t.guards)


def _effects(law: ForbiddenEffects, t: Transition) -> bool:
    return bool(set(law.effects) & set(t.required_effects)) or not set(law.effects) <= set(t.forbidden_effects)


def _final(law: StateFinal, t: Transition) -> bool:
    return t.from_state == law.state


_TRANSITION_CHECKS: dict[type, Callable[[Any, Transition], bool]] = {
    OnlyRoleHolds: _only_role, RoleNeverHolds: _never_role, RoleNeverEnters: _never_enters,
    StateOnlyVia: _only_via, ActionTarget: _target, ActionSourceIn: _source,
    ActionRequiresGuard: _guard, ForbiddenEffects: _effects, StateFinal: _final,
}


# ---- whole-table laws ---------------------------------------------------------------------------------------

def _shape_breaks(law: ClosedShape, model: Workflow) -> bool:
    actions = {t.action for t in model.transitions}
    return actions != set(law.actions) or set(model.states) != set(law.states) or model.initial_state != law.initial_state


def reachable(edges: Iterable[tuple[str, str]], start: str, blocked: str | None = None) -> set[str]:
    """States reachable from ``start`` without passing through ``blocked`` (cycle-safe)."""
    graph: dict[str, set[str]] = {}
    for source, target in edges:
        graph.setdefault(source, set()).add(target)
    seen, frontier = {start}, [start]
    while frontier:
        node = frontier.pop()
        for nxt in sorted(graph.get(node, set()) - seen):
            if nxt != blocked:
                seen.add(nxt)
                frontier.append(nxt)
    return seen


def _path_breaks(law: PathRequires, model: Workflow) -> bool:
    if law.via in (model.initial_state, law.state):
        return False
    edges = [(t.from_state, t.to_state) for t in model.transitions]
    return law.state in reachable(edges, model.initial_state, blocked=law.via)


def _table_violation(law: _Law, model: Workflow) -> Violation | None:
    if isinstance(law, ClosedShape) and _shape_breaks(law, model):
        return Violation(law.id, law.code, ("law:" + law.id,))
    if isinstance(law, PathRequires) and _path_breaks(law, model):
        return Violation(law.id, law.code, ("law:" + law.id, "state:" + law.state))
    return None


def evaluate_table(laws: Sequence[_Law], model: Workflow) -> list[Violation]:
    """Every violation of the applicable laws by the workflow's transition table, in law order."""
    actions = {t.action for t in model.transitions}
    found: list[Violation] = []
    for law in laws:
        if not applies(law, actions):
            continue
        whole = _table_violation(law, model)
        if whole is not None:
            found.append(whole)
        found += [Violation(law.id, law.code, ("law:" + law.id, "transition:" + t.id))
                  for t in model.transitions if _breaks(law, t)]
    return found


def _as_transition(step: Step, index: int) -> Transition:
    return Transition.model_construct(id=f"STEP-{index}", action=step.action, from_state=step.source, to_state=step.target,
                                      role=step.role, guards=(), required_effects=step.effects, forbidden_effects=())


def _run_path_breaks(law: PathRequires, initial: str, steps: Sequence[Step]) -> bool:
    visited = {initial}
    for step in steps:
        if step.target == law.state and law.via not in visited and law.state != law.via:
            return True
        visited.add(step.target)
    return False


def evaluate_run(laws: Sequence[_Law], initial: str, steps: Sequence[Step], actions: set[str]) -> list[Violation]:
    """Violations by one executed run: per-step laws on every step, sequence laws on the whole run.

    ``actions`` is the action set of the workflow the run executed (for ``when`` conditions). Structural laws
    (``closed_shape``) and evidence requirements are about the table, not a run, and are not judged here. Only
    a step's REQUIRED effects are known, so the ``forbidden_effects`` law judges that nothing forbidden ran."""
    found: list[Violation] = []
    for law in laws:
        if not applies(law, actions):
            continue
        if isinstance(law, PathRequires) and _run_path_breaks(law, initial, steps):
            found.append(Violation(law.id, law.code, ("law:" + law.id, "state:" + law.state)))
        found += [Violation(law.id, law.code, ("law:" + law.id, f"step:{i}"))
                  for i, step in enumerate(steps) if _step_breaks(law, _as_transition(step, i))]
    return found


def _step_breaks(law: _Law, t: Transition) -> bool:
    if isinstance(law, ForbiddenEffects):
        return bool(set(law.effects) & set(t.required_effects))
    return _breaks(law, t)
