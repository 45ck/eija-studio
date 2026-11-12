"""Generic execution algorithm; the domain (policy, laws, typed effects) comes from the pack."""
from __future__ import annotations
from typing import Any, Callable
from uuid import uuid4
from eija_studio.domain.laws import DistinctActors, applies, separation_breach
from eija_studio.domain.models import Workflow, ExecuteCommand, DomainError, Transition, fingerprint
from eija_studio.domain.pack import Pack, default_pack
from eija_studio.domain.policy import ensure_policy
from .memo import ensure_conforms, model_hash
from .ports import UnitOfWork


def check_actor(actor: dict[str, Any], transition: Transition, command: ExecuteCommand) -> None:
    if not actor["active"]:
        raise DomainError("ACTOR_REVOKED", "Actor is not active at commit time")
    if actor["role"] != transition.role:
        raise DomainError("ROLE_DENIED", "Actor does not hold the current required role")
    if "actor_assigned" in transition.guards and not actor["assigned"]:
        raise DomainError("ASSIGNMENT_DENIED", "Actor is not assigned in the trusted fixture directory")


def separations(pack: Pack, model: Workflow, action: str) -> list[DistinctActors]:
    """The pack's separation-of-duties laws in force on ``model`` that name ``action`` (issue #149, ADR-0233)."""
    actions = {t.action for t in model.transitions}
    return [law for law in pack.laws if isinstance(law, DistinctActors) and action in law.actions and applies(law, actions)]


def check_separation(laws: list[DistinctActors], action: str, actor_id: str, acts: list[tuple[str, str]]) -> None:
    """Refuse an actor who already took another action of a separation law on this record. ``acts`` is the record's
    (action, actor) history as the unit of work recorded it."""
    for law in laws:
        earlier = separation_breach(law, action, actor_id, acts)
        if earlier is not None:
            raise DomainError("SEPARATION_DENIED", f"The same actor may not {action} after they {earlier} on this record",
                              {"codes": [law.code], "refs": [f"law:{law.id}", f"action:{earlier}", f"action:{action}"]})


def check_guards(transition: Transition, values: dict[str, Any]) -> None:
    """Refuse a transition whose guards over the record's values do not hold (ADR-0234). Missing values fail closed."""
    failed = transition.admits(values)
    if failed is not None:
        raise DomainError("VALUE_GUARD_DENIED", f"{transition.action} needs [{failed}]",
                          {"codes": ["VALUE_GUARD_DENIED"], "refs": [f"transition:{transition.id}", f"attribute:{failed.attribute}"]})


def check_due(transition: Transition, elapsed: float | None) -> None:
    """Refuse a transition with a time event, ``after(14 days)``, before the record has been in its source state that
    long (ADR-0237). An unknown entry time is never due (fail closed)."""
    if transition.after is not None and not transition.after.due(elapsed):
        raise DomainError("TIMER_NOT_DUE", f"{transition.action} is due only {transition.after} in {transition.from_state}",
                          {"codes": ["TIMER_NOT_DUE"], "refs": [f"transition:{transition.id}", f"state:{transition.from_state}"]})


def check_linked(model: Workflow, transition: Transition, states: dict[str, str | None]) -> list[dict[str, str]]:
    """The moves a transition makes on the objects the record links to, given each object's state (ADR-0241). Refuses
    the whole step when an object is unknown, its state is, or its lifecycle has no move for the event from there."""
    moves = []
    for step in transition.then:
        lifecycle, state = model.lifecycle(step.link), states.get(step.link)
        target = lifecycle.move(step.event, state) if lifecycle is not None else None
        if target is None or state is None:
            raise DomainError("LINKED_OBJECT_REFUSED", f"{transition.action} needs {step} but {step.link} is {state or 'unknown'}",
                              {"codes": ["LINKED_OBJECT_REFUSED"], "refs": [f"transition:{transition.id}", f"link:{step.link}"]})
        moves.append({"link": step.link, "event": step.event, "from": state, "to": target})
    return moves


def _admitted(session: UnitOfWork, model: Workflow, transition: Transition, instance_id: str) -> list[dict[str, str]]:
    """Read the record's clock only for a transition with a time event, its values only for one with value guards and
    its linked objects only for one that moves them; most transitions touch none. Returns the objects' moves."""
    if transition.after is not None:
        check_due(transition, session.elapsed(instance_id))
    if transition.conditions:
        check_guards(transition, session.values(instance_id))
    if not transition.then:
        return []
    return check_linked(model, transition, {s.link: session.object_state(instance_id, s.link) for s in transition.then})


def _separate(session: UnitOfWork, laws: list[DistinctActors], action: str, actor_id: str, instance_id: str) -> None:
    """Refuse or log this act for the separation laws naming the action; with none (most packs) the log is untouched."""
    if laws:
        check_separation(laws, action, actor_id, session.acts(instance_id))
        session.record_act(instance_id, action, actor_id)


def _perform(session: UnitOfWork, pack: Pack, effect: str, case_id: str, command: ExecuteCommand, result: dict[str, Any]) -> None:
    """Run one declared effect through its typed adapter: audit log or outbox. An undeclared effect is refused."""
    declared = pack.effect(effect)
    if declared is None:
        raise DomainError("EFFECT_DENIED", "No adapter exists for this effect")
    if declared.kind == "audit":
        session.event(effect, {"case_id": case_id, "operation_id": command.operation_id, "actor_id": command.actor_id,
                               "instance_id": command.instance_id, "result": result})
    else:
        session.enqueue(case_id, command.operation_id, effect, declared.recipient or "")


def _enter(session: UnitOfWork, instance: dict[str, Any], t: Transition, expected: int, moves: list[dict[str, str]]) -> None:
    """Move the record to the transition's target and its linked objects with it, in the same unit of work (ADR-0241)."""
    instance.update(state=t.to_state, version=instance["version"] + 1)
    session.update_instance(instance, expected)
    for move in moves:
        session.move_object(instance["id"], move["link"], move["to"])


def _committed(instance: dict[str, Any], t: Transition, moves: list[dict[str, str]]) -> dict[str, Any]:
    """The result of a committed step; `moved` only for a step on a linked object, so other results keep their bytes."""
    result = {"duplicate": False, "committed": True, "instance": instance, "effects": list(t.required_effects)}
    return result | ({"moved": moves} if moves else {})


def initialise(session: UnitOfWork, case_id: str, model: Workflow, *, state: str | None = None,
               pack: Pack | None = None, role: str | None = None) -> dict[str, Any]:
    """Start a record. With ``role`` (the creator's role) a model that names its initiators refuses anyone else
    (ADR-0231); without it the caller is a preview or oracle that starts records on the kernel's behalf."""
    ensure_conforms(model, pack if pack is not None else default_pack(), ensure_policy)
    if role is not None and model.initiators and role not in model.initiators:
        raise DomainError("ROLE_CANNOT_START", f"{role} may not start a record; the model names who may: {', '.join(model.initiators)}",
                          {"codes": ["ROLE_CANNOT_START"], "refs": [f"role:{r}" for r in model.initiators]})
    state = state or model.initial_state
    if state not in model.states:
        raise DomainError("INVALID_STATE", "State is not in the current model")
    item = {"id": uuid4().hex, "case_id": case_id, "model_hash": model_hash(model), "state": state, "version": 0}
    session.create_instance(item)
    return item


def execute(
    session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *,
    fault: Callable[[str], None] | None = None, pack: Pack | None = None,
) -> dict[str, Any]:
    pack = pack if pack is not None else default_pack()
    ensure_conforms(model, pack, ensure_policy)  # the policy check, asked once per model and pack object (ADR-0199)
    row = session.find_instance(command.instance_id, case_id)
    if row is None:
        raise DomainError("NOT_FOUND", "Preview instance not found in this case")
    instance = dict(row)
    if instance["model_hash"] != model_hash(model):
        raise DomainError("STALE_INSTANCE", "Model changed; reset the isolated preview")
    t = model.transition_for(command.action, instance["state"])
    if t is None:
        raise DomainError("ACTION_DENIED", "Action is not modelled")
    actor = session.actor(command.actor_id)
    # Authorise BEFORE lookup/replay. A cached success is not continuing authority.
    check_actor(actor, t, command)
    binding = fingerprint({"case": case_id, "subject": model_hash(model), "command": command.model_dump(mode="json")})
    prior = session.find_operation(command.operation_id)
    if prior is not None:
        if prior["binding"] != binding:
            raise DomainError("OPERATION_CONFLICT", "Operation id is already bound to another request")
        return {"duplicate": True, "committed": False, "instance": instance,
                "original_result": prior["result"], "effects": []}
    if instance["version"] != command.expected_version:
        raise DomainError("STALE_VERSION", "Instance changed; reload before acting")
    if instance["state"] != t.from_state:
        raise DomainError("STATE_DENIED", "Action is invalid from the current state")
    moves = _admitted(session, model, t, instance["id"])
    _separate(session, separations(pack, model, t.action), t.action, command.actor_id, instance["id"])
    _enter(session, instance, t, command.expected_version, moves)
    if fault:
        fault("after_state")
    result = _committed(instance, t, moves)
    for effect in t.required_effects:
        _perform(session, pack, effect, case_id, command, result)
    if fault:
        fault("after_effects")
    session.record_operation(command.operation_id, binding, result)
    if fault:
        fault("after_operation")
    return result  # HTTP success is sent only after the enclosing unit of work commits.


def receive(session: UnitOfWork, case_id: str, model: Workflow, signal: str, sender: str, operation_id: str, *,
            pack: Pack | None = None, values: dict[str, Any] | None = None) -> dict[str, Any]:
    """Start a record because another workflow of the system sent `signal` (issue #93 item 5, ADR-0242).

    The sender's step put the signal in its outbox in its own unit of work; delivering it here is a separate unit of
    work, so the sender is never refused by the receiver. A signal the model does not say it receives from `sender` is
    refused with SIGNAL_NOT_ACCEPTED. The operation id makes a redelivery start nothing new: the same signal, sender and
    record `values` return the original record, and anything else under that id is OPERATION_CONFLICT."""
    pack = pack if pack is not None else default_pack()
    ensure_conforms(model, pack, ensure_policy)
    if model.receiving(signal, sender) is None:
        raise DomainError("SIGNAL_NOT_ACCEPTED", f"This workflow does not start a record on {signal} from {sender}",
                          {"refs": [f"signal:{signal}", f"workflow:{sender}"]})
    binding = fingerprint({"case": case_id, "subject": model_hash(model), "signal": signal, "sender": sender,
                           "values": values or {}})
    prior = session.find_operation(operation_id)
    if prior is not None:
        if prior["binding"] != binding:
            raise DomainError("OPERATION_CONFLICT", "Operation id is already bound to another request")
        return {"duplicate": True, "started": False, "original_result": prior["result"]}
    item = initialise(session, case_id, model, pack=pack)
    result = {"duplicate": False, "started": True, "instance": item, "signal": signal, "sender": sender}
    session.record_operation(operation_id, binding, result)
    return result
