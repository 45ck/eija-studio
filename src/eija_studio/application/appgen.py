"""App generation: a reviewed workflow model becomes a runnable app and its conformance oracle (ADR-0150).

The generated app is storage, HTTP and a page from fixed templates (`resources/appgen/`). It has no rules of its own: it
calls the kernel's `runtime.execute` and `runtime.initialise` through a SQLite unit of work, on the `app/model.json` and
`app/pack.json` written here. `tests/oracle.json` holds the kernel's answer for every case on an in-memory session, so
the app passes only if its storage, transactions and effects keep the kernel's behaviour end to end.

Pure: no IO, no clock, no randomness. The same pack and model always give byte-identical files.
"""
from __future__ import annotations

from itertools import product
from typing import Any

from eija_studio.domain.data import Attribute, DataModel, check_record, record_fields, references
from eija_studio.domain.laws import DistinctActors
from eija_studio.domain.models import DomainError, Transition, ValueGuard, Workflow, canonical, fingerprint
from eija_studio.domain.navigation import navigation_for
from eija_studio.domain.pack import Pack
from eija_studio.domain.policy import check_policy
from eija_studio.domain.screens import Screens, default_screens, require_buildable
from eija_studio.domain.value_guards import MAX_VALUATIONS, combinations, guard_problems
from .app_runs import create_cases, journeys, options_cases, rules
from .oracle_session import UNKNOWN_ACTOR, OracleSession as _OracleSession, absent, kernel_answer as _kernel

FORMAT = "eija.app-build.v1"
# The oracle's case lists beside `cases`, each checked by its own generated test (ADR-0241 added the last three).
CASE_KINDS = ("data_cases", "start_cases", "separation_cases", "value_cases", "timer_cases", "create_cases", "journeys",
              "options_cases")
UNDECLARED_ACTION = "UndeclaredAction"
LIMITS = (
    "The app runs the EIJA kernel itself (eija-studio must be installed). Records created under an earlier model are "
    "refused with STALE_INSTANCE, and under an earlier data model with STALE_DATA.",
    "Actors are the pack's fixture directory chosen in the UI. That is not authentication.",
    "Notifications are written to an outbox table; nothing is sent.",
    "Conformance covers every state x action x fixture actor x version case, plus replays, record creation, a run to "
    "each transition and the actions offered, through the service and over HTTP, against the kernel. "
    "It is exhaustive for this model and these actors, not a proof about other inputs.",
)


NO_DATA = "Records carry a title only: this pack has no data model (data.json)."
WITH_DATA = ("Record values are checked against the record entity's attributes. Other entities and associations are "
             "shown in the class diagram but not stored yet.")
SAMPLES = {"text": "Sample", "number": 1, "date": "2026-01-15", "boolean": True}
WRONG = {"text": 123, "number": "not a number", "date": "15/01/2026", "boolean": "yes"}


def app_limits(data: DataModel | None) -> list[str]:
    return [LIMITS[0], WITH_DATA if data else NO_DATA, *LIMITS[1:]]


def _sample(attribute: Attribute) -> object:
    """A valid value: the first choice, or the type's sample, cut to the attribute's length (a 4-digit card suffix)."""
    if attribute.type == "choice":
        return attribute.choices[0]
    sample = SAMPLES[attribute.type]
    return sample[:attribute.max_length] if isinstance(sample, str) and attribute.type == "text" else sample


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


def _fits(attribute: Attribute, valid: dict[str, object]) -> list[tuple[str, dict[str, object]]]:
    """Values at the edge of what one attribute accepts, starting from a valid record: text exactly as long as it may
    be, and every declared choice, so a narrower rule in the app is caught as surely as a looser one."""
    name = attribute.name
    if attribute.type == "text":
        return [(f"{name} at its limit", valid | {name: "x" * attribute.max_length})]
    if attribute.type == "choice":
        return [(f"{name} is {choice}", valid | {name: choice}) for choice in attribute.choices[1:]]
    return []


def _answer(data: DataModel, values: dict[str, object], stored: set[tuple[str, str]]) -> dict[str, object]:
    try:
        return {"outcome": "CREATED", "fields": check_record(data, values, lambda c, i: (c, i) in stored)}
    except DomainError as refused:
        return {"outcome": "REFUSED", "code": refused.code}


def may_start(model: Workflow, role: str) -> bool:
    """Whether the model lets this role start a record (ADR-0231): any role when it names no initiators."""
    return not model.initiators or role in model.initiators


def start_cases(pack: Pack, model: Workflow) -> list[dict[str, object]]:
    """Each active fixture actor starting a record, and the kernel's answer. Only for a model that names initiators,
    so the oracle of every other model keeps its exact bytes."""
    if not model.initiators:
        return []
    return [{"actor": a.id, "expect": {"outcome": "CREATED"} if may_start(model, a.role) else {"outcome": "REFUSED", "code": "ROLE_CANNOT_START"}}
            for a in sorted(pack.fixtures.actors, key=lambda a: a.id) if a.active]


def _separated_pairs(pack: Pack, model: Workflow) -> list[tuple[Transition, str]]:
    """Each transition of a separation-of-duties law's action, with each other action of the law that leaves where it ends."""
    follows = {(t.from_state, t.action) for t in model.transitions}
    return sorted({(t, then) for law in pack.laws if isinstance(law, DistinctActors) for t in model.transitions
                   if t.action in law.actions for then in law.actions if then != t.action and (t.to_state, then) in follows},
                  key=lambda pair: (pair[0].id, pair[1]))


def separation_cases(pack: Pack, model: Workflow) -> list[dict[str, object]]:
    """One fixture actor takes an action of a separation-of-duties law, then tries another the law names, on the same
    record; the kernel's answer to the second (ADR-0233). Only where the actor's role may take both, since otherwise
    the role check refuses first. Empty without such a law, so every other oracle keeps its exact bytes."""
    cases: list[dict[str, object]] = []
    for t, then in _separated_pairs(pack, model):
        second = model.transition_for(then, t.to_state)
        for actor in sorted(pack.fixtures.actors, key=lambda a: a.id):
            if second is None or actor.role != second.role:
                continue
            session = _OracleSession(pack, model, t.from_state)
            if _kernel(pack, model, session, actor.id, t.action, 0)["outcome"] == "COMMITTED":
                cases.append({"state": t.from_state, "actor": actor.id, "first": t.action, "then": then,
                              "expect": _kernel(pack, model, session, actor.id, then, 1, "op-2")})
    return cases


def _taker(pack: Pack, t: Transition) -> str | None:
    """The first fixture actor the kernel lets take this transition, value guards aside."""
    return next((a.id for a in sorted(pack.fixtures.actors, key=lambda a: a.id) if a.active and a.role == t.role
                 and (a.assigned or "actor_assigned" not in t.guards)), None)


def value_cases(pack: Pack, model: Workflow) -> list[dict[str, object]]:
    """For each transition with guards over record values, an actor who may take it tries it on records holding every
    combination of values its guards can tell apart (`value_guards.combinations`), and the kernel's answer (ADR-0234).
    Empty for a model without value guards, so every other oracle keeps its exact bytes."""
    cases: list[dict[str, object]] = []
    for t in sorted((t for t in model.transitions if t.conditions), key=lambda t: t.id):
        actor = _taker(pack, t)
        if actor is None:
            continue
        grouped: dict[str, list[ValueGuard]] = {}
        for guard in t.conditions:
            grouped.setdefault(guard.attribute, []).append(guard)
        tried = combinations(dict(sorted(grouped.items())))
        if tried is None:  # never a silently empty check: the build is refused instead
            raise DomainError("VALUE_GUARD_TOO_MANY", f"{t.id} has guards over too many combinations of values to check "
                              f"(more than {MAX_VALUATIONS}); no app is built", {"refs": [f"transition:{t.id}"]})
        for values in tried:
            session = _OracleSession(pack, model, t.from_state, values)
            case: dict[str, Any] = {"state": t.from_state, "action": t.action, "actor": actor, "values": values,
                    "expect": _kernel(pack, model, session, actor, t.action, 0)}
            if case["expect"]["outcome"] == "COMMITTED":
                case["written"] = {"audit": list(session.audited), "outbox": [list(q) for q in session.queued]}
            cases.append(case)
    return cases


def timer_cases(pack: Pack, model: Workflow) -> list[dict[str, object]]:
    """For each transition with a time event, an actor who may take it tries it on a record that has been in the source
    state half the time and the whole time, and the kernel's answer (ADR-0237). Empty for a model without time events,
    so every other oracle keeps its exact bytes."""
    cases: list[dict[str, object]] = []
    for t in sorted((t for t in model.transitions if t.after is not None), key=lambda t: t.id):
        actor = _taker(pack, t)
        if actor is None or t.after is None:
            continue
        for waited in (t.after.seconds / 2, float(t.after.seconds)):
            session = _OracleSession(pack, model, t.from_state, _admitting(t), waited)
            cases.append({"state": t.from_state, "action": t.action, "actor": actor, "waited": waited,
                          **({"values": _admitting(t)} if t.conditions else {}),
                          "expect": _kernel(pack, model, session, actor, t.action, 0)})
    return cases


def _admitting(t: Transition) -> dict[str, Any]:
    """Record values every value guard of `t` admits, when some combination does; {} otherwise."""
    grouped: dict[str, list[ValueGuard]] = {}
    for guard in t.conditions:
        grouped.setdefault(guard.attribute, []).append(guard)
    return next((v for v in combinations(dict(sorted(grouped.items()))) or [] if t.admits(v) is None), {})


def _people_cases(pack: Pack, model: Workflow) -> dict[str, Any]:
    """The oracle's checks of who may start a record and who may not act twice, present only when the model or pack
    asks for them, so every other oracle keeps its exact bytes."""
    found = {"separation_cases": separation_cases(pack, model), "value_cases": value_cases(pack, model),
             "timer_cases": timer_cases(pack, model)}
    return ({"start_cases": start_cases(pack, model)} if model.initiators else {}) | {k: v for k, v in found.items() if v}


def _creator(pack: Pack, model: Workflow | None) -> str:
    """The first active fixture actor the model lets start a record."""
    creator = next((a.id for a in pack.fixtures.actors if a.active and (model is None or may_start(model, a.role))), None)
    if creator is None:
        raise DomainError("NO_ACTIVE_ACTOR", "No fixture actor is active, so nobody could create a record; no app is built")
    return creator


def stock(data: DataModel) -> list[dict[str, object]]:
    """One valid object of each class a record refers to (ADR-0235), stored before the data cases run. Empty when no
    association is built, so other oracles keep their exact bytes."""
    classes = sorted({r.target for r in references(data)})
    return [{"class": c, "id": f"obj{n}", "fields": {a.name: _sample(a) for a in data.entity(c).attributes}}
            for n, c in enumerate(classes, start=1)]


def _reference_breaks(data: DataModel, valid: dict[str, object]) -> list[tuple[str, dict[str, object]]]:
    """Ways to get a reference field wrong: missing when required, not an id, and the id of no stored object."""
    tries = []
    for ref in references(data):
        if ref.required:
            tries.append((f"{ref.name} missing", {k: v for k, v in valid.items() if k != ref.name}))
        tries += [(f"{ref.name} wrong type", valid | {ref.name: 123}), (f"{ref.name} unknown", valid | {ref.name: "nothing"})]
    return tries


def data_cases(pack: Pack, data: DataModel, model: Workflow | None = None) -> list[dict[str, object]]:
    """Record values to create with, and `check_record`'s answer for each: a valid record, then each required value
    missing, each value of the wrong type, each text one character too long, an undeclared choice and an unknown field,
    then each reference field missing, not an id and naming no stored object (with the `stock` objects stored)."""
    entity = data.entity(data.record)
    creator = _creator(pack, model)
    stored = {(str(o["class"]), str(o["id"])) for o in stock(data)}
    valid = valid_values(data)
    least = {f.name: valid[f.name] for f in record_fields(data) if f.required}
    tries = [("valid", valid), *(bad for a in entity.attributes for bad in _breaks(a, valid)),
             ("unknown field", valid | {absent("extra", {a.name for a in record_fields(data)}): "x"}),
             *_reference_breaks(data, valid),
             # Appended after the cases above so their order holds: the edges of each rule, then only required values.
             *(edge for a in entity.attributes for edge in _fits(a, valid)), ("required values only", least)]
    cases: list[dict[str, Any]] = [{"name": name, "actor": creator, "fields": values, "expect": _answer(data, values, stored)}
                                   for name, values in tries]
    return _require_valid(cases, data)


def _require_valid(cases: list[dict[str, Any]], data: DataModel) -> list[dict[str, Any]]:
    """Never a suite whose "valid" record the app must refuse: that would leave every create check vacuous."""
    if cases[0]["expect"]["outcome"] != "CREATED":
        raise DomainError("DATA_NO_VALID_RECORD", f"The sample record is refused ({cases[0]['expect'].get('code')}); no app is built",
                          {"refs": [f"class:{data.record}"]})
    return cases


def valid_values(data: DataModel | None) -> dict[str, object]:
    """A valid record: a sample of each attribute, and each reference naming the first `stock` object of its class."""
    if data is None:
        return {}
    stored = sorted((str(o["class"]), str(o["id"])) for o in stock(data))
    return {a.name: _sample(a) for a in data.entity(data.record).attributes} | {
        r.name: next(i for c, i in stored if c == r.target) for r in references(data)}


def oracle_cases(pack: Pack, model: Workflow) -> list[dict[str, Any]]:
    """Every state x action x actor x expected version, then the same request replayed. The kernel answers each.

    One undeclared action and one unknown actor, both proven absent from this model and fixture directory, are the
    negative controls for the missing-resolver refusals (ACTION_DENIED, UNKNOWN_ACTOR)."""
    declared_actions = {t.action for t in model.transitions} | {a.id for a in pack.actions}
    declared_actors = {a.id for a in pack.fixtures.actors}
    actions = [*sorted({t.action for t in model.transitions}), absent(UNDECLARED_ACTION, declared_actions)]
    actors = [*sorted(declared_actors), absent(UNKNOWN_ACTOR, declared_actors)]
    cases = []
    for state, action, actor, version in product(sorted(model.states), actions, actors, (0, 1)):
        session = _OracleSession(pack, model, state)
        first = _kernel(pack, model, session, actor, action, version)
        case = {"state": state, "action": action, "actor": actor, "expected_version": version, "expect": first}
        if first["outcome"] == "COMMITTED":
            case["written"] = {"audit": list(session.audited), "outbox": [list(q) for q in session.queued]}
            case["replay"] = _kernel(pack, model, session, actor, action, version)
            # the same request under a new operation id: not a replay, so the kernel judges it afresh
            case["again"] = _kernel(pack, model, session, actor, action, version, "op-2")
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


def _require_policy(pack: Pack, model: Workflow) -> None:
    """Refuse a workflow from another pack, or one the protected policy blocks."""
    if model.id != pack.id:
        raise DomainError("WORKFLOW_PACK_MISMATCH", f"Workflow {model.id!r} does not belong to pack {pack.id!r}")
    errors = check_policy(model, pack)
    if errors:
        raise DomainError("POLICY_BLOCKED", "The protected policy refuses this workflow; no app is built",
                          {"codes": sorted(errors)})


def _require_data(pack: Pack, model: Workflow, data: DataModel | None) -> None:
    """Refuse a data model from another pack, or value guards that do not fit its record class (ADR-0234)."""
    if data is not None and data.id != pack.id:
        raise DomainError("DATA_PACK_MISMATCH", f"Data model {data.id!r} does not belong to pack {pack.id!r}")
    problems = guard_problems(model, data)
    if problems:
        raise DomainError("VALUE_GUARD_INVALID", "A guard over record values does not fit the data model; no app is built",
                          {"codes": problems})


def generate(pack: Pack, model: Workflow | None = None, data: DataModel | None = None,
             screens: Screens | None = None) -> tuple[dict[str, str], dict[str, Any]]:
    """Return the per-model files and the build manifest (without file hashes or test results).

    Refuses a model the protected policy blocks: an app is never built from a workflow the kernel would refuse. Nor from
    screens with design problems (ADR-0154); without screens, each use case gets a default one."""
    model = model if model is not None else pack.model
    _require_policy(pack, model)
    _require_data(pack, model, data)
    screens = screens if screens is not None else default_screens(pack, model, data)
    if screens.id != pack.id:
        raise DomainError("SCREENS_PACK_MISMATCH", f"Screens {screens.id!r} do not belong to pack {pack.id!r}")
    require_buildable(screens, model, data)
    cases = oracle_cases(pack, model)
    oracle: dict[str, Any] = {"format": "eija.app-oracle.v1", "model_hash": model.semantic_hash,
                              "source": "eija_studio runtime.execute", "cases": cases, "screens_digest": screens.digest}
    navigation = navigation_for(pack, model, data, screens)
    files = {"app/model.json": canonical(model) + "\n", "app/pack.json": canonical(pack) + "\n",
             "app/screens.json": canonical(screens) + "\n",
             "app/navigation.json": canonical(navigation) + "\n",
             "README.md": readme(pack, model, len(cases), data)}
    if data is not None:
        oracle |= {"data_digest": data.digest, "data_cases": data_cases(pack, data, model)}
        oracle |= {"objects": stock(data)} if references(data) else {}
        files["app/data.json"] = canonical(data) + "\n"
    oracle |= _people_cases(pack, model)
    oracle |= {"waited": model.longest_wait} if model.longest_wait else {}  # how long ordinary cases' records waited
    valid = valid_values(data)
    oracle |= {"create_cases": create_cases(pack, model), "journeys": journeys(pack, model, valid),
               "options_cases": options_cases(pack, model, valid), "rules": rules(model)}
    files["tests/oracle.json"] = canonical(oracle) + "\n"
    total = len(cases) + sum(len(oracle.get(k, [])) for k in CASE_KINDS)
    manifest = {"format": FORMAT, "pack": {"id": pack.id, "version": pack.pack.version, "digest": pack.digest},
                "model_semantic_hash": model.semantic_hash, "oracle": {"cases": total, "hash": fingerprint(oracle)},
                "data": {"digest": data.digest, "record": data.record} if data else None,
                "screens": {"digest": screens.digest, "count": len(screens.screens)}, "limits": app_limits(data)}
    return files, manifest
