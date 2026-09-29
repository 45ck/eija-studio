"""Open change vocabulary (WBS 1.3): the semantic edits an owner (or a pack meaning) may make to a workflow.

A transaction is a small typed record, a discriminated union on ``kind``. ``apply_structural`` applies one to a
workflow and returns the new workflow; it checks structure only (the element exists, the result is a coherent
workflow). Whether the result is ALLOWED is the policy's job (``domain.policy.apply_transactions``), so a refusal
names the law it breaks. Nothing here names a domain: states, roles and actions come from the model and the pack.

Terms (``rename_term``/``bind_term``) are not in this vocabulary yet: a term lives in the pack's language, not in
a case's workflow, and binding needs the weave index (WBS 1.6). See docs/engineering/FUTURE-WORK.md.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Annotated, Any, Literal, Union

from pydantic import ConfigDict, Field, RootModel, ValidationError

from .models import Contract, DomainError, Guard, Transition, Workflow

Name = Annotated[str, Field(min_length=1, max_length=60)]
TransitionId = Annotated[str, Field(pattern=r"^[A-Z][A-Z0-9_-]{0,63}$")]


class AddState(Contract):
    kind: Literal["add_state"]
    state: Name
    after: Name | None = None  # insert after this state (order is presentation only); None appends


class RenameState(Contract):
    kind: Literal["rename_state"]
    state: Name
    to: Name


class RemoveState(Contract):
    kind: Literal["remove_state"]
    state: Name


class SetInitial(Contract):
    kind: Literal["set_initial"]
    state: Name


class AddTransition(Contract):
    """A transition performing a declared action; its guards and effects are the action's declared ones."""
    kind: Literal["add_transition"]
    id: TransitionId
    action: Name
    from_state: Name
    to_state: Name
    role: Name


class RetargetTransition(Contract):
    """Move one end of a transition to another state (the drag-and-drop edit)."""
    kind: Literal["retarget_transition"]
    transition: TransitionId
    end: Literal["source", "target"]
    state: Name


class RemoveTransition(Contract):
    kind: Literal["remove_transition"]
    transition: TransitionId


class SetRole(Contract):
    kind: Literal["set_role"]
    transition: TransitionId
    role: Name


class SetGuards(Contract):
    kind: Literal["set_guards"]
    transition: TransitionId
    guards: tuple[Guard, ...] = Field(min_length=1, max_length=8)


class SetEffects(Contract):
    kind: Literal["set_effects"]
    transition: TransitionId
    required_effects: tuple[Name, ...] = Field(max_length=16)


Transaction = Annotated[Union[AddState, RenameState, RemoveState, SetInitial, AddTransition,  # noqa: UP007
                              RetargetTransition, RemoveTransition, SetRole, SetGuards, SetEffects],
                        Field(discriminator="kind")]
TRANSACTION_KINDS = ("add_state", "rename_state", "remove_state", "set_initial", "add_transition", "retarget_transition",
                     "remove_transition", "set_role", "set_guards", "set_effects")


class TransactionDocument(RootModel[Transaction]):
    """One semantic transaction as a JSON document (contracts/semantic-transaction.schema.json)."""
    model_config = ConfigDict(frozen=True)


def parse_transaction(data: Any) -> Transaction:
    """Validate one transaction document; a malformed one is ``EDIT_INVALID``, never a crash."""
    if not isinstance(data, dict) or data.get("kind") not in TRANSACTION_KINDS:
        raise DomainError("EDIT_INVALID", "Unknown or missing transaction kind", details={"codes": ["EDIT_INVALID"], "refs": []})
    try:
        return TransactionDocument.model_validate(data).root
    except ValidationError:
        raise DomainError("EDIT_INVALID", "Transaction fields are invalid", details={"codes": ["EDIT_INVALID"], "refs": []}) from None


# ---- structural application ---------------------------------------------------------------------------------

Declare = Callable[[str, str, str, str, str], Transition]  # (id, action, source, target, role) -> declared transition


def refused(code: str, message: str, *refs: str) -> DomainError:
    return DomainError(code, message, details={"codes": [code], "refs": sorted(refs)})


def _find(model: Workflow, transition_id: str) -> Transition:
    found = next((t for t in model.transitions if t.id == transition_id), None)
    if found is None:
        raise refused("EDIT_INVALID", "No such transition", "transition:" + transition_id)
    return found


def _need_state(model: Workflow, state: str) -> None:
    if state not in model.states:
        raise refused("EDIT_INVALID", "No such state", "state:" + state)


def _replace(model: Workflow, transition_id: str, **changes: Any) -> dict[str, Any]:
    data = model.model_dump(mode="json")
    for t in data["transitions"]:
        if t["id"] == transition_id:
            t.update({k: list(v) if isinstance(v, tuple) else v for k, v in changes.items()})
    return data


def _add_state(model: Workflow, tx: AddState, _: Declare) -> dict[str, Any]:
    if tx.state in model.states:
        raise refused("EDIT_INVALID", "State already exists", "state:" + tx.state)
    states = list(model.states)
    if tx.after is not None:
        _need_state(model, tx.after)
    states.insert(states.index(tx.after) + 1 if tx.after is not None else len(states), tx.state)
    return model.model_dump(mode="json") | {"states": states}


def _rename_state(model: Workflow, tx: RenameState, _: Declare) -> dict[str, Any]:
    _need_state(model, tx.state)
    if tx.to in model.states:
        raise refused("EDIT_INVALID", "Target state name already exists", "state:" + tx.to)
    data = model.model_dump(mode="json")
    rename = {tx.state: tx.to}
    data["states"] = [rename.get(s, s) for s in data["states"]]
    data["initial_state"] = rename.get(data["initial_state"], data["initial_state"])
    for t in data["transitions"]:
        t["from_state"], t["to_state"] = rename.get(t["from_state"], t["from_state"]), rename.get(t["to_state"], t["to_state"])
    return data


def _remove_state(model: Workflow, tx: RemoveState, _: Declare) -> dict[str, Any]:
    _need_state(model, tx.state)
    users = [t.id for t in model.transitions if tx.state in (t.from_state, t.to_state)]
    if users or tx.state == model.initial_state:
        raise refused("EDIT_INVALID", "State is still in use", "state:" + tx.state, *("transition:" + u for u in users))
    return model.model_dump(mode="json") | {"states": [s for s in model.states if s != tx.state]}


def _set_initial(model: Workflow, tx: SetInitial, _: Declare) -> dict[str, Any]:
    _need_state(model, tx.state)
    return model.model_dump(mode="json") | {"initial_state": tx.state}


def _add_transition(model: Workflow, tx: AddTransition, declare: Declare) -> dict[str, Any]:
    new = declare(tx.id, tx.action, tx.from_state, tx.to_state, tx.role)
    data = model.model_dump(mode="json")
    data["transitions"].append(new.model_dump(mode="json"))
    return data


def _retarget(model: Workflow, tx: RetargetTransition, _: Declare) -> dict[str, Any]:
    _find(model, tx.transition)
    _need_state(model, tx.state)
    return _replace(model, tx.transition, **{"from_state" if tx.end == "source" else "to_state": tx.state})


def _remove_transition(model: Workflow, tx: RemoveTransition, _: Declare) -> dict[str, Any]:
    _find(model, tx.transition)
    data = model.model_dump(mode="json")
    data["transitions"] = [t for t in data["transitions"] if t["id"] != tx.transition]
    return data


def _set_role(model: Workflow, tx: SetRole, _: Declare) -> dict[str, Any]:
    _find(model, tx.transition)
    return _replace(model, tx.transition, role=tx.role)


def _set_guards(model: Workflow, tx: SetGuards, _: Declare) -> dict[str, Any]:
    _find(model, tx.transition)
    return _replace(model, tx.transition, guards=tx.guards)


def _set_effects(model: Workflow, tx: SetEffects, _: Declare) -> dict[str, Any]:
    _find(model, tx.transition)
    return _replace(model, tx.transition, required_effects=tx.required_effects)


_APPLY: dict[type, Callable[[Workflow, Any, Declare], dict[str, Any]]] = {
    AddState: _add_state, RenameState: _rename_state, RemoveState: _remove_state, SetInitial: _set_initial,
    AddTransition: _add_transition, RetargetTransition: _retarget, RemoveTransition: _remove_transition,
    SetRole: _set_role, SetGuards: _set_guards, SetEffects: _set_effects,
}


def element_refs(tx: Transaction) -> tuple[str, ...]:
    """The model elements a transaction names (for refusal details)."""
    refs = [f"transition:{getattr(tx, name)}" for name in ("transition", "id") if isinstance(getattr(tx, name, None), str)]
    return tuple(refs + [f"state:{getattr(tx, name)}" for name in ("state",) if isinstance(getattr(tx, name, None), str)])


def apply_structural(model: Workflow, tx: Transaction, declare: Declare) -> Workflow:
    """``model`` with ``tx`` applied. Structural defects (unknown element, incoherent result) are ``EDIT_INVALID``."""
    data = _APPLY[type(tx)](model, tx, declare)
    try:
        return Workflow.model_validate(data)
    except ValidationError:
        raise refused("EDIT_INVALID", "The edit would make the workflow incoherent", *element_refs(tx)) from None
