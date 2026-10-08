"""Bounded synthetic runtime experiments. Not a theorem prover or human study."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4
from eija_studio.domain.models import Workflow, ExecuteCommand, DomainError, Transition, fingerprint
from eija_studio.domain.pack import Actor, Pack, default_pack
from .runtime import initialise, execute
from .ports import SandboxFactory, UnitOfWork

# The oracle is the pack's transition table read with the fixture directory: an actor may perform an action from a
# state iff the action is modelled from that state, the actor is active and holds the transition's role, and (when
# the transition carries the assignment guard) is assigned. It is computed separately from the runtime's guard
# evaluation, but shares the pack's authorship: it is not an independently blinded oracle.


def __getattr__(name: str) -> Any:
    """``ACTORS``: the default pack's fixture directory as (id, role, active, assigned). Kept only for
    verification/bend/bend_generate.py, whose bytes the committed Bend proof binds; WBS 1.4 regenerates that proof."""
    if name == "ACTORS":
        return tuple((a.id, a.role, a.active, a.assigned) for a in default_pack().fixtures.actors)
    raise AttributeError(name)


def _allowed(actor: Actor, state: str, t: Transition | None) -> bool:
    return (t is not None and actor.active and actor.role == t.role and state == t.from_state
            and ("actor_assigned" not in t.guards or actor.assigned))


def _expected(actor: Actor, state: str, t: Transition | None, pack: Pack) -> dict[str, Any]:
    allowed = _allowed(actor, state, t)
    kinds = [] if t is None or not allowed else [e.kind for x in t.required_effects if (e := pack.effect(x)) is not None]
    return {"accepted": allowed, "state": t.to_state if allowed and t is not None else state,
            "version": int(allowed), "audit": kinds.count("audit"), "outbox": kinds.count("notification"),
            "operations": int(allowed)}


def _observe(store: Any, model: Workflow, actor: Actor, state: str, action: str, pack: Pack) -> dict[str, Any]:
    with store.transaction() as u:
        item = initialise(u, "oracle", model, state=state, pack=pack)
        before = u.effect_counts()
    command = ExecuteCommand(operation_id=uuid4().hex, actor_id=actor.id, instance_id=item["id"], action=action, expected_version=0)
    accepted = False
    try:
        with store.transaction() as u:
            execute(u, "oracle", model, command, pack=pack)
        accepted = True
    except DomainError:
        pass
    with store.transaction() as u:
        after = _instance(u, item["id"])
        counts = u.effect_counts()
    return {"accepted": accepted, "state": after["state"], "version": after["version"],
            **{k: counts[k] - before[k] for k in ("audit", "outbox", "operations")}}


def _instance(u: UnitOfWork, instance_id: str) -> dict[str, Any]:
    after = u.find_instance(instance_id, "oracle")
    assert after is not None, "the fixture instance was just initialised in this sandbox"  # noqa: S101
    return after


def verify_runtime(model: Workflow, subject: dict[str, Any], sandbox: SandboxFactory, pack: Pack | None = None) -> dict[str, Any]:
    pack = pack if pack is not None else default_pack()
    by = {t.action: t for t in model.transitions}
    actions = [a.id for a in pack.actions]
    with sandbox() as store:
        cells = [{"actor": actor.id, "state": state, "action": action,
                  "expected": _expected(actor, state, by.get(action), pack),
                  "actual": _observe(store, model, actor, state, action, pack)}
                 for actor in pack.fixtures.actors for state in model.states for action in actions]
    artifact = {"protocol": "bounded-runtime-matrix-v1", "expected_cells": len(pack.fixtures.actors) * len(model.states) * len(actions),
                "matrix": {"actors": [a.id for a in pack.fixtures.actors], "states": list(model.states), "actions": actions},
                "cells": cells, "limitations": ["Synthetic fixture directory; no real SSO", "No human-outcome measurement",
                "One-step state/action matrix, not exhaustive arbitrary sequences", "Same-author oracle, not an independent holdout",
                "Disposable non-durable sandbox: observes transaction semantics, not crash durability"]}
    return {"id": uuid4().hex, "claim": "runtime_matrix", "kind": "integration_test", "subject": subject,
            "producer": "eija-local-verifier", "method": artifact["protocol"], "created_at": datetime.now(timezone.utc).isoformat(),
            "artifact_hash": fingerprint(artifact), "artifact": artifact}
