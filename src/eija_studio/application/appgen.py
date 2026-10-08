"""App generation: a reviewed workflow model becomes a runnable app and its conformance oracle (ADR-0150).

The generated app is storage, HTTP and a page from fixed templates (`resources/appgen/`). It has no rules of its own: it
calls the kernel's `runtime.execute` and `runtime.initialise` through a SQLite unit of work, on the `app/model.json` and
`app/pack.json` written here. `tests/oracle.json` holds the kernel's answer for every case on an in-memory session, so
the app passes only if its storage, transactions and effects keep the kernel's behaviour end to end.

Pure: no IO, no clock, no randomness. The same pack and model always give byte-identical files.
"""
from __future__ import annotations

from itertools import count, product
from typing import Any

from eija_studio.domain.data import Attribute, DataModel, Entity, check_values
from eija_studio.domain.models import DomainError, ExecuteCommand, Workflow, canonical, fingerprint
from eija_studio.domain.pack import Pack
from eija_studio.domain.policy import check_policy
from eija_studio.domain.screens import Screens, default_screens, require_buildable
from .runtime import execute

FORMAT = "eija.app-build.v1"
UNDECLARED_ACTION = "UndeclaredAction"
UNKNOWN_ACTOR = "unknown-actor"
LIMITS = (
    "The app runs the EIJA kernel itself (eija-studio must be installed). Records created under an earlier model are "
    "refused with STALE_INSTANCE, and under an earlier data model with STALE_DATA.",
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


def absent(base: str, taken: set[str]) -> str:
    """A name guaranteed not to be in `taken`, so a negative case can never collide with a declared one."""
    return next(name for name in (base if n == 0 else f"{base}{n}" for n in count()) if name not in taken)


NO_DATA = "Records carry a title only: this pack has no data model (data.json)."
WITH_DATA = ("Record values are checked against the record entity's attributes. Other entities and associations are "
             "shown in the class diagram but not stored yet.")
SAMPLES = {"text": "Sample", "number": 1, "date": "2026-01-15", "boolean": True}
WRONG = {"text": 123, "number": "not a number", "date": "15/01/2026", "boolean": "yes"}


def app_limits(data: DataModel | None) -> list[str]:
    return [LIMITS[0], WITH_DATA if data else NO_DATA, *LIMITS[1:]]


def _sample(attribute: Attribute) -> object:
    return attribute.choices[0] if attribute.type == "choice" else SAMPLES[attribute.type]


def _breaks(attribute: Attribute, valid: dict[str, object]) -> list[tuple[str, dict[str, object]]]:
    """Ways to get one attribute wrong, starting from a valid record."""
    name, tries = attribute.name, []
    if attribute.required:
        tries.append((f"{name} missing", {k: v for k, v in valid.items() if k != name}))
    if attribute.type == "choice":
        tries.append((f"{name} not a choice", valid | {name: absent("Other", set(attribute.choices))}))
    else:
        tries.append((f"{name} wrong type", valid | {name: WRONG[attribute.type]}))
    if attribute.type == "text":
        tries.append((f"{name} too long", valid | {name: "x" * (attribute.max_length + 1)}))
    return tries


def _answer(entity: Entity, values: dict[str, object]) -> dict[str, object]:
    try:
        return {"outcome": "CREATED", "fields": check_values(entity, values)}
    except DomainError as refused:
        return {"outcome": "REFUSED", "code": refused.code}


def data_cases(pack: Pack, data: DataModel) -> list[dict[str, object]]:
    """Record values to create with, and `check_values`' answer for each: a valid record, then each required value
    missing, each value of the wrong type, each text one character too long, an undeclared choice and an unknown field."""
    entity = data.entity(data.record)
    creator = next((a.id for a in pack.fixtures.actors if a.active), None)
    if creator is None:
        raise DomainError("NO_ACTIVE_ACTOR", "No fixture actor is active, so nobody could create a record; no app is built")
    valid = {a.name: _sample(a) for a in entity.attributes}
    tries = [("valid", valid), *(bad for a in entity.attributes for bad in _breaks(a, valid)),
             ("unknown field", valid | {absent("extra", {a.name for a in entity.attributes}): "x"})]
    return [{"name": name, "actor": creator, "fields": values, "expect": _answer(entity, values)} for name, values in tries]


def oracle_cases(pack: Pack, model: Workflow) -> list[dict[str, Any]]:
    """Every state x action x actor x expected version, then the same request replayed. The kernel answers each.

    One undeclared action and one unknown actor, both proven absent from this model and fixture directory, are the
    negative controls for the missing-resolver refusals (ACTION_DENIED, UNKNOWN_ACTOR)."""
    declared_actions = {t.action for t in model.transitions} | {a.id for a in pack.actions}
    declared_actors = {a.id for a in pack.fixtures.actors}
    actions = [*sorted(t.action for t in model.transitions), absent(UNDECLARED_ACTION, declared_actions)]
    actors = [*sorted(declared_actors), absent(UNKNOWN_ACTOR, declared_actors)]
    cases = []
    for state, action, actor, version in product(sorted(model.states), actions, actors, (0, 1)):
        session = _OracleSession(pack, model, state)
        first = _kernel(pack, model, session, actor, action, version)
        case = {"state": state, "action": action, "actor": actor, "expected_version": version, "expect": first}
        if first["outcome"] == "COMMITTED":
            case["replay"] = _kernel(pack, model, session, actor, action, version)
        cases.append(case)
    return cases


def readme(pack: Pack, model: Workflow, cases: int, data: DataModel | None = None) -> str:
    rows = "\n".join(f"| {t.action} | {t.from_state} | {t.to_state} | {t.role} |" for t in model.transitions)
    lines = "\n".join(f"- {line}" for line in app_limits(data))
    return f"""# {pack.pack.name}

Generated by EIJA Studio from model `{model.semantic_hash[:12]}` (pack `{pack.id}` {pack.pack.version}).
Do not edit the generated files. Change the model and run `eija build` again.

{pack.pack.description}

## Run it

```bash
python run.py            # http://127.0.0.1:8000, data in data/app.sqlite3
python -m unittest       # {cases} conformance cases against the EIJA kernel's answers
```

Run it with a Python that has `eija-studio` installed: the app's rules are the EIJA kernel itself.

## What it does

| Action | From | To | Role |
|---|---|---|---|
{rows}

## Limits

{lines}
"""


def generate(pack: Pack, model: Workflow | None = None, data: DataModel | None = None,
             screens: Screens | None = None) -> tuple[dict[str, str], dict[str, Any]]:
    """Return the per-model files and the build manifest (without file hashes or test results).

    Refuses a model the protected policy blocks: an app is never built from a workflow the kernel would refuse. Nor from
    screens with design problems (ADR-0154); without screens, each use case gets a default one."""
    model = model if model is not None else pack.model
    if model.id != pack.id:
        raise DomainError("WORKFLOW_PACK_MISMATCH", f"Workflow {model.id!r} does not belong to pack {pack.id!r}")
    errors = check_policy(model, pack)
    if errors:
        raise DomainError("POLICY_BLOCKED", "The protected policy refuses this workflow; no app is built",
                          {"codes": sorted(errors)})
    if data is not None and data.id != pack.id:
        raise DomainError("DATA_PACK_MISMATCH", f"Data model {data.id!r} does not belong to pack {pack.id!r}")
    screens = screens if screens is not None else default_screens(pack, model, data)
    if screens.id != pack.id:
        raise DomainError("SCREENS_PACK_MISMATCH", f"Screens {screens.id!r} do not belong to pack {pack.id!r}")
    require_buildable(screens, model, data)
    cases = oracle_cases(pack, model)
    oracle: dict[str, Any] = {"format": "eija.app-oracle.v1", "model_hash": model.semantic_hash,
                              "source": "eija_studio runtime.execute", "cases": cases, "screens_digest": screens.digest}
    files = {"app/model.json": canonical(model) + "\n", "app/pack.json": canonical(pack) + "\n",
             "app/screens.json": canonical(screens) + "\n",
             "README.md": readme(pack, model, len(cases), data)}
    if data is not None:
        oracle |= {"data_digest": data.digest, "data_cases": data_cases(pack, data)}
        files["app/data.json"] = canonical(data) + "\n"
    files["tests/oracle.json"] = canonical(oracle) + "\n"
    total = len(cases) + len(oracle.get("data_cases", []))
    manifest = {"format": FORMAT, "pack": {"id": pack.id, "version": pack.pack.version, "digest": pack.digest},
                "model_semantic_hash": model.semantic_hash, "oracle": {"cases": total, "hash": fingerprint(oracle)},
                "data": {"digest": data.digest, "record": data.record} if data else None,
                "screens": {"digest": screens.digest, "count": len(screens.screens)}, "limits": app_limits(data)}
    return files, manifest
