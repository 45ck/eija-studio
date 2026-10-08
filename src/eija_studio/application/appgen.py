"""App generation: a reviewed workflow model becomes the spec and the conformance oracle of a runnable app (ADR-0150).

The generated app's runtime is a fixed template (`resources/appgen/`); what changes per model is `app/spec.py`, written
here as plain Python literals that read like the diagram, and `tests/oracle.json`. The oracle is not this module's
reading of the model: every case is answered by the kernel's own `runtime.execute` against an in-memory session, so the
generated app passes its tests only if it refuses and commits exactly where the kernel does.

Pure: no IO, no clock, no randomness. The same pack and model always give byte-identical files.
"""
from __future__ import annotations

from itertools import product
from pprint import pformat
from typing import Any

from eija_studio.domain.models import DomainError, ExecuteCommand, Workflow, canonical, fingerprint
from eija_studio.domain.pack import Pack
from eija_studio.domain.policy import check_policy
from .runtime import execute

FORMAT = "eija.app-build.v1"
UNDECLARED_ACTION = "UndeclaredAction"
UNKNOWN_ACTOR = "unknown-actor"
LIMITS = (
    "The app implements the workflow's states, roles, guards and declared effects. Records carry a title only; "
    "entities and fields are not modelled yet.",
    "Actors are the pack's fixture directory chosen in the UI. That is not authentication.",
    "Notifications are written to an outbox table; nothing is sent.",
    "Conformance covers every state x action x fixture actor x version case, plus replays, against the kernel. "
    "It is exhaustive for this model and these actors, not a proof about other inputs.",
)


class _OracleSession:
    """In-memory answers to exactly the port calls `execute` makes for one instance. Nothing persists."""

    def __init__(self, pack: Pack, model: Workflow, state: str):
        self.actors = {a.id: a.model_dump() for a in pack.fixtures.actors}
        self.item = {"id": "r1", "case_id": "app", "model_hash": model.semantic_hash, "state": state, "version": 0}
        self.operations: dict[str, dict[str, Any]] = {}

    def find_instance(self, instance_id: str, case_id: str) -> dict[str, Any] | None:
        return self.item if instance_id == self.item["id"] else None

    def actor(self, actor_id: str) -> dict[str, Any]:
        if actor_id not in self.actors:
            raise DomainError("UNKNOWN_ACTOR", "Actor is not in the trusted fixture directory")
        return self.actors[actor_id]

    def find_operation(self, operation_id: str) -> dict[str, Any] | None:
        return self.operations.get(operation_id)

    def update_instance(self, item: dict[str, Any], expected: int) -> None:
        self.item = dict(item)

    def record_operation(self, operation_id: str, binding: str, result: dict[str, Any]) -> None:
        self.operations[operation_id] = {"binding": binding, "result": result}

    def event(self, kind: str, body: dict[str, Any]) -> None:
        return None

    def enqueue(self, case_id: str, operation_id: str, effect: str, recipient: str) -> None:
        return None


def _kernel(pack: Pack, model: Workflow, session: _OracleSession, actor: str, action: str, version: int) -> dict[str, Any]:
    command = ExecuteCommand(operation_id="op-1", actor_id=actor, instance_id="r1", action=action, expected_version=version)
    try:
        result = execute(session, "app", model, command, pack=pack)  # type: ignore[arg-type]  # duck-typed session
    except DomainError as refused:
        return {"outcome": "REFUSED", "code": refused.code}
    if result["duplicate"]:
        return {"outcome": "DUPLICATE", "state": result["instance"]["state"]}
    return {"outcome": "COMMITTED", "state": result["instance"]["state"], "effects": result["effects"]}


def oracle_cases(pack: Pack, model: Workflow) -> list[dict[str, Any]]:
    """Every state x action x actor x expected version, then the same request replayed. The kernel answers each."""
    actions = [*sorted(t.action for t in model.transitions), UNDECLARED_ACTION]
    actors = [*sorted(a.id for a in pack.fixtures.actors), UNKNOWN_ACTOR]
    cases = []
    for state, action, actor, version in product(sorted(model.states), actions, actors, (0, 1)):
        session = _OracleSession(pack, model, state)
        first = _kernel(pack, model, session, actor, action, version)
        case = {"state": state, "action": action, "actor": actor, "expected_version": version, "expect": first}
        if first["outcome"] == "COMMITTED":
            case["replay"] = _kernel(pack, model, session, actor, action, version)
        cases.append(case)
    return cases


def _spec(pack: Pack, model: Workflow) -> dict[str, Any]:
    effects = {e.id: {"kind": e.kind, "recipient": e.recipient or ""} for e in pack.effects.catalog}
    return {
        "APP_NAME": pack.pack.name,
        "APP_DESCRIPTION": pack.pack.description,
        "PACK_ID": pack.id,
        "PACK_VERSION": pack.pack.version,
        "MODEL_HASH": model.semantic_hash,
        "INITIAL_STATE": model.initial_state,
        "STATES": tuple(model.states),
        "TRANSITIONS": {t.action: {"id": t.id, "from": t.from_state, "to": t.to_state, "role": t.role,
                                   "guards": tuple(t.guards), "effects": tuple(t.required_effects)}
                        for t in model.transitions},
        "ROLES": {r.id: r.description for r in pack.roles},
        "ACTORS": {a.id: {"role": a.role, "active": a.active, "assigned": a.assigned} for a in pack.fixtures.actors},
        "EFFECTS": {e: effects[e] for e in sorted({e for t in model.transitions for e in t.required_effects})},
    }


def spec_source(pack: Pack, model: Workflow) -> str:
    lines = [f'"""Generated by EIJA Studio from model {model.semantic_hash[:12]} ({pack.id} {pack.pack.version}).',
             "", "Do not edit. Change the model in EIJA Studio and run `eija build` again; the conformance tests in",
             'tests/ fail if this file and the model disagree."""', ""]
    for name, value in _spec(pack, model).items():
        lines.append(f"{name} = {pformat(value, width=110, sort_dicts=False)}")
    return "\n".join(lines) + "\n"


def readme(pack: Pack, model: Workflow, cases: int) -> str:
    rows = "\n".join(f"| {t.action} | {t.from_state} | {t.to_state} | {t.role} |" for t in model.transitions)
    limits = "\n".join(f"- {line}" for line in LIMITS)
    return f"""# {pack.pack.name}

Generated by EIJA Studio from model `{model.semantic_hash[:12]}` (pack `{pack.id}` {pack.pack.version}).
Do not edit the generated files. Change the model and run `eija build` again.

{pack.pack.description}

## Run it

```bash
python run.py            # http://127.0.0.1:8000, data in data/app.sqlite3
python -m unittest       # {cases} conformance cases against the EIJA kernel's answers
```

It needs Python 3.11 or newer and nothing else.

## What it does

| Action | From | To | Role |
|---|---|---|---|
{rows}

## Limits

{limits}
"""


def generate(pack: Pack, model: Workflow | None = None) -> tuple[dict[str, str], dict[str, Any]]:
    """Return the per-model files and the build manifest (without file hashes or test results).

    Refuses a model the protected policy blocks: an app is never built from a workflow the kernel would refuse."""
    model = model if model is not None else pack.model
    errors = check_policy(model, pack)
    if errors:
        raise DomainError("POLICY_BLOCKED", "The protected policy refuses this workflow; no app is built",
                          {"codes": sorted(errors)})
    cases = oracle_cases(pack, model)
    oracle = {"format": "eija.app-oracle.v1", "model_hash": model.semantic_hash, "source": "eija_studio runtime.execute",
              "cases": cases}
    files = {"app/spec.py": spec_source(pack, model), "tests/oracle.json": canonical(oracle) + "\n",
             "README.md": readme(pack, model, len(cases))}
    manifest = {"format": FORMAT, "pack": {"id": pack.id, "version": pack.pack.version, "digest": pack.digest},
                "model_semantic_hash": model.semantic_hash, "oracle": {"cases": len(cases), "hash": fingerprint(oracle)},
                "limits": list(LIMITS)}
    return files, manifest
