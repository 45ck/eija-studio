"""Generic execution algorithm; domain-specific policy stays in domain.policy."""
from __future__ import annotations
from uuid import uuid4
from eija_studio.domain.models import Workflow, ExecuteCommand, DomainError, fingerprint
from eija_studio.domain.policy import ensure_policy
from .ports import UnitOfWork


def check_actor(actor: dict, transition, command: ExecuteCommand) -> None:
    if not actor["active"]:
        raise DomainError("ACTOR_REVOKED", "Actor is not active at commit time")
    if actor["role"] != transition.role:
        raise DomainError("ROLE_DENIED", "Actor does not hold the current required role")
    if "actor_assigned" in transition.guards and not actor["assigned"]:
        raise DomainError("ASSIGNMENT_DENIED", "Actor is not assigned in the trusted fixture directory")


def initialise(session: UnitOfWork, case_id: str, model: Workflow, *, state: str | None = None) -> dict:
    ensure_policy(model)
    state = state or model.initial_state
    if state not in model.states:
        raise DomainError("INVALID_STATE", "State is not in the current model")
    item = {"id": uuid4().hex, "case_id": case_id, "model_hash": model.semantic_hash, "state": state, "version": 0}
    session.create_instance(item)
    return item


def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault=None) -> dict:
    ensure_policy(model)
    row = session.find_instance(command.instance_id, case_id)
    if row is None:
        raise DomainError("NOT_FOUND", "Preview instance not found in this case")
    instance = dict(row)
    if instance["model_hash"] != model.semantic_hash:
        raise DomainError("STALE_INSTANCE", "Model changed; reset the isolated preview")
    t = next((t for t in model.transitions if t.action == command.action), None)
    if t is None:
        raise DomainError("ACTION_DENIED", "Action is not modelled")
    actor = session.actor(command.actor_id)
    # Authorise BEFORE lookup/replay. A cached success is not continuing authority.
    check_actor(actor, t, command)
    binding = fingerprint({"case": case_id, "subject": model.semantic_hash, "command": command.model_dump(mode="json")})
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
    instance.update(state=t.to_state, version=instance["version"] + 1)
    session.update_instance(instance, command.expected_version)
    if fault:
        fault("after_state")
    result = {"duplicate": False, "committed": True, "instance": instance, "effects": list(t.required_effects)}
    for effect in t.required_effects:
        if effect.startswith("Audit:"):
            session.event(effect, {"case_id": case_id, "operation_id": command.operation_id, "actor_id": command.actor_id,
                                   "instance_id": command.instance_id, "result": result})
        elif effect.startswith("Notification:"):
            session.enqueue(case_id, command.operation_id, effect)
        else:
            raise DomainError("EFFECT_DENIED", "No adapter exists for this effect")
    if fault:
        fault("after_effects")
    session.record_operation(command.operation_id, binding, result)
    if fault:
        fault("after_operation")
    return result  # HTTP success is sent only after the enclosing unit of work commits.
