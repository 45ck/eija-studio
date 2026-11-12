"""Seeded divergence: does a generated app's own conformance suite fail whenever the app stops matching its model?

`eija build` claims the app commits and refuses exactly where the kernel does on the reviewed model. This checks the
claim from the other side. For every shipped pack (and a few feature variants no shipped pack uses yet) it builds real
apps that are wrong in exactly one way and runs each one's generated tests (`tests/test_conformance.py`) in a fresh
process, as `eija build` does:

* **Model divergence.** The app is built from a model, data model or pack that differs from the reviewed one in one
  element: a transition dropped, moved to another source or target, given another role; a guard, required effect,
  value guard, initial state or initiator changed; an effect's kind or recipient changed; a fixture actor's standing
  changed; a record attribute's rule changed; a separation-of-duties law dropped. The app keeps the reviewed oracle
  and tests. Only the identity fields (model hash, data and screens digests) are re-pointed at the divergent app, and
  the build identity is resealed, so a hash check can never be what catches it: only behaviour can.
* **Code divergence.** One seeded fault in the app's own code (`app/service.py`, `app/server.py`), resealed the same way.

Each divergence is CAUGHT (the generated suite fails), REFUSED (no app is built: the model is invalid or the protected
policy refuses it), or MISSED. A MISSED divergence is a hole in the claim unless it is listed in `EQUIVALENT` with the
reason it cannot change what the app does. Each law of the pack is also checked: every model divergence the law proof
finds BROKEN for that law must be CAUGHT or REFUSED.

    python -m verification.conformance.divergence [--pack NAME ...] [--out reports/conformance/divergence.json]

Exit codes: 0 PASS (nothing MISSED that is not equivalent), 1 FAIL.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter
from collections.abc import Callable, Iterator
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from importlib.resources import files as resource_files
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from pydantic import ValidationError

from eija_studio.application.appgen import generate
from eija_studio.application.build_subject import SUBJECT_FILE, build_subject
from eija_studio.application.generated_app import TEMPLATES
from eija_studio.application.law_proof import prove_laws
from eija_studio.bootstrap import implementation_manifest
from eija_studio.domain.data import DataModel, data_for
from eija_studio.domain.laws import DistinctActors
from eija_studio.domain.models import DomainError, Workflow, canonical, fingerprint
from eija_studio.domain.pack import Pack, PackError, load_pack, parse_pack
from eija_studio.domain.screens import default_screens

FORMAT = "eija.conformance-divergence.v1"
CORE = ("library-loan", "refund-desk+features", "library-loan+features")  # every element kind and feature, quickly
ROOT = Path(__file__).resolve().parents[2]
TIMEOUT_S = 300
STATIC = {target: resource_files("eija_studio.resources").joinpath("appgen", source).read_text(encoding="utf-8")
          for source, target in TEMPLATES.items()}
IMPLEMENTATION = fingerprint(implementation_manifest())

# Divergences that cannot change what the app does, with the reason. Nothing else may be MISSED.
EQUIVALENT = {
    "forbidden-effect-dropped": "The kernel performs only a transition's required effects, so a forbidden effect is "
                                "never performed either way. The protected policy checks forbidden effects when the "
                                "model is built (POLICY_BLOCKED), before any app exists.",
}


@dataclass(frozen=True)
class Subject:
    """One reviewed app: a pack, the model built from it and its data model."""
    name: str
    pack: Pack
    model: Workflow
    data: DataModel | None


@dataclass(frozen=True)
class Divergence:
    """One way the app differs from the reviewed model. `kind` groups them; `ref` names the model element."""
    kind: str
    ref: str
    text: str
    pack: Pack | None = None
    model: Workflow | None = None
    data: DataModel | None = None
    code: tuple[str, str, str] | None = None  # (file, before, after) for a code divergence
    refused: str | None = None  # why no app could be built from it


@dataclass
class Outcome:
    divergence: Divergence
    status: str
    failed: list[str] = field(default_factory=list)
    detail: str = ""


# ---------------------------------------------------------------------------------------------------- subjects


def shipped() -> list[Subject]:
    found = []
    for directory in sorted(p for p in (ROOT / "packs").iterdir() if (p / "pack.json").is_file()):
        pack = load_pack(directory)
        found.append(Subject(directory.name, pack, pack.model, data_for(pack)))
    return found


def _variant_pack(pack: Pack, **changes: Any) -> Pack:
    return parse_pack(pack.model_dump(mode="json") | changes)


def variants() -> list[Subject]:
    """Kernel features no shipped pack uses yet, so their generated tests are not vacuous: initiators (ADR-0231),
    separation of duties (ADR-0233) and value guards (ADR-0234) on refund-desk; built references (ADR-0235) and one action
    from two states (ADR-0232) on library-loan."""
    desk = load_pack(ROOT / "packs" / "refund-desk")
    laws = [law.model_dump(mode="json") for law in desk.laws] + [
        {"id": "assessor-does-not-propose", "kind": "distinct_actors", "code": "SAME_ASSESSOR",
         "actions": ["AssessRequest", "ProposeRefund"], "description": "Whoever assesses a request does not propose it."}]
    raw = desk.model.model_dump(mode="json") | {"initiators": ["Customer"]}
    for t in raw["transitions"]:
        if t["action"] == "ApproveRefund":
            t["conditions"] = [{"attribute": "amount", "op": "le", "value": 500}]
    model = Workflow.model_validate(raw)
    pack = _variant_pack(desk, laws=laws, model=raw)
    loan = load_pack(ROOT / "packs" / "library-loan")
    data = data_for(loan)
    built = data.model_dump(mode="json")  # type: ignore[union-attr]  # library-loan has a data model
    for association in built["associations"]:
        if association["source"] == built["record"]:
            association["built"] = True  # Loan -> Copy and Loan -> Member become reference fields (ADR-0235)
    lent = loan.model.model_dump(mode="json")  # `Return` also leaves Overdue, in place of ReturnLate (ADR-0232)
    back = next(t for t in lent["transitions"] if t["action"] == "Return")
    lent["transitions"] = [t for t in lent["transitions"] if t["action"] != "ReturnLate"] + [
        back | {"id": "TR-RETURN-OVERDUE", "from_state": "Overdue"}]
    return [Subject("refund-desk+features", pack, model, data_for(desk)),
            Subject("library-loan+features", loan, Workflow.model_validate(lent), DataModel.model_validate(built))]


# ---------------------------------------------------------------------------------------------------- divergences


def _workflow(model: Workflow, change: Callable[[dict[str, Any]], None]) -> Workflow | str:
    raw = model.model_dump(mode="json")
    change(raw)
    try:
        return Workflow.model_validate(raw)
    except ValidationError as invalid:
        return f"INVALID_MODEL: {invalid.errors()[0]['msg']}"


def _transition(raw: dict[str, Any], tid: str) -> dict[str, Any]:
    return next(t for t in raw["transitions"] if t["id"] == tid)


def _other(choices: list[str], *avoid: str) -> str | None:
    return next((c for c in choices if c not in avoid), None)


def _linked_divergences(model: Workflow) -> Iterator[tuple[str, str, str, Workflow | str]]:
    """A linked object's lifecycle changed: it starts in another state, or one of its moves leads elsewhere (ADR-0241)."""
    for n, obj in enumerate(model.objects):
        ref = f"object:{obj.link}"
        start = _other(sorted(obj.states), obj.initial)
        if start is not None:
            yield "object-initial-moved", f"{ref}/initial", f"{obj.link} starts {start}, not {obj.initial}", _workflow(
                model, lambda raw, i=n, v=start: raw["objects"][i].__setitem__("initial", v))
        for m, move in enumerate(obj.moves):
            elsewhere = _other(sorted(obj.states), move.to_state, move.from_state)
            if elsewhere is not None:
                yield "object-move-retargeted", f"{ref}/{move.event}", \
                    f"{obj.link}.{move.event} leads to {elsewhere}, not {move.to_state}", _workflow(
                    model, lambda raw, i=n, j=m, v=elsewhere: raw["objects"][i]["moves"][j].__setitem__("to_state", v))


def _model_divergences(s: Subject) -> Iterator[tuple[str, str, str, Workflow | str]]:
    model, states = s.model, sorted(s.model.states)
    roles = sorted({r.id for r in s.pack.roles} | {t.role for t in model.transitions})
    catalog = [e.id for e in s.pack.effects.catalog]
    for t in sorted(model.transitions, key=lambda t: t.id):
        ref, tid = f"transition:{t.id}", t.id
        yield "transition-dropped", ref, f"{t.action} from {t.from_state} is missing", _workflow(
            model, lambda raw, tid=tid: raw.__setitem__("transitions", [x for x in raw["transitions"] if x["id"] != tid]))
        for target in states:
            if target != t.to_state:
                yield "target-moved", ref, f"{t.action} leads to {target}, not {t.to_state}", _workflow(
                    model, lambda raw, tid=tid, v=target: _transition(raw, tid).__setitem__("to_state", v))
        source = _other(states, t.from_state, *model.sources(t.action))
        if source is not None:
            yield "source-moved", ref, f"{t.action} leaves {source}, not {t.from_state}", _workflow(
                model, lambda raw, tid=tid, v=source: _transition(raw, tid).__setitem__("from_state", v))
        for role in roles:
            if role != t.role:
                yield "role-changed", ref, f"{t.action} is taken by {role}, not {t.role}", _workflow(
                    model, lambda raw, tid=tid, v=role: _transition(raw, tid).__setitem__("role", v))
        if "actor_assigned" in t.guards:
            yield "guard-dropped", ref, f"{t.action} no longer needs an assigned actor", _workflow(
                model, lambda raw, tid=tid: _transition(raw, tid).__setitem__(
                    "guards", [g for g in _transition(raw, tid)["guards"] if g != "actor_assigned"]))
        else:
            yield "guard-added", ref, f"{t.action} needs an assigned actor", _workflow(
                model, lambda raw, tid=tid: _transition(raw, tid)["guards"].append("actor_assigned"))
        for effect in t.required_effects:
            yield "effect-dropped", f"{ref}/effect:{effect}", f"{t.action} skips {effect}", _workflow(
                model, lambda raw, tid=tid, v=effect: _transition(raw, tid).__setitem__(
                    "required_effects", [e for e in _transition(raw, tid)["required_effects"] if e != v]))
        extra = _other(catalog, *t.required_effects, *t.forbidden_effects)
        if extra is not None:
            yield "effect-added", f"{ref}/effect:{extra}", f"{t.action} also performs {extra}", _workflow(
                model, lambda raw, tid=tid, v=extra: _transition(raw, tid)["required_effects"].append(v))
        for effect in t.forbidden_effects:
            yield "forbidden-effect-dropped", f"{ref}/forbidden:{effect}", f"{t.action} no longer forbids {effect}", _workflow(
                model, lambda raw, tid=tid, v=effect: _transition(raw, tid).__setitem__(
                    "forbidden_effects", [e for e in _transition(raw, tid)["forbidden_effects"] if e != v]))
        if t.after is not None:
            yield "time-event-dropped", f"{ref}/after", f"{t.action} no longer waits {t.after.span}", _workflow(
                model, lambda raw, tid=tid: _transition(raw, tid).pop("after"))
            longer = min(10_000, t.after.amount * 2)
            yield "time-event-lengthened", f"{ref}/after", f"{t.action} waits {longer} {t.after.unit}", _workflow(
                model, lambda raw, tid=tid, v=longer: _transition(raw, tid)["after"].update(amount=v))
        for n, guard in enumerate(t.conditions):
            yield "value-guard-dropped", f"{ref}/when:{guard}", f"{t.action} no longer needs [{guard}]", _workflow(
                model, lambda raw, tid=tid, i=n: _transition(raw, tid)["conditions"].pop(i))
            flipped = {"eq": "ne", "ne": "eq", "lt": "ge", "le": "gt", "gt": "le", "ge": "lt"}[guard.op]
            yield "value-guard-flipped", f"{ref}/when:{guard}", f"{t.action} needs the opposite of [{guard}]", _workflow(
                model, lambda raw, tid=tid, i=n, v=flipped: _transition(raw, tid)["conditions"][i].__setitem__("op", v))
        for n, step in enumerate(t.then):
            yield "linked-step-dropped", f"{ref}/then:{step}", f"{t.action} no longer does {step}", _workflow(
                model, lambda raw, tid=tid, i=n: _transition(raw, tid)["then"].pop(i))
    yield from _linked_divergences(model)
    for state in states:
        if state != model.initial_state:
            yield "initial-state-moved", "model:initial_state", f"records start in {state}, not {model.initial_state}", \
                _workflow(model, lambda raw, tid=tid, v=state: raw.__setitem__("initial_state", v))
            break
    starters = sorted({a.role for a in s.pack.fixtures.actors if a.active})
    if model.initiators:
        for role in model.initiators:
            yield "initiator-dropped", f"model:initiators/{role}", f"{role} may no longer start a record", _workflow(
                model, lambda raw, v=role: raw.__setitem__("initiators", [r for r in raw["initiators"] if r != v] or [
                    _other(starters, *raw["initiators"])]))
        widened = _other(starters, *model.initiators)
        if widened is not None:
            yield "initiator-added", f"model:initiators/{widened}", f"{widened} may also start a record", _workflow(
                model, lambda raw, v=widened: raw["initiators"].append(v))
    elif len(starters) > 1:
        yield "initiators-narrowed", "model:initiators", f"only {starters[0]} may start a record", _workflow(
            model, lambda raw: raw.__setitem__("initiators", [starters[0]]))


def _pack_change(s: Subject, change: Callable[[dict[str, Any]], None]) -> Pack | str:
    raw = s.pack.model_dump(mode="json")
    change(raw)
    try:
        return parse_pack(raw)
    except PackError as invalid:
        return f"INVALID_PACK: {invalid.diagnostics[0]}"


def _effect(raw: dict[str, Any], eid: str) -> dict[str, Any]:
    return next(e for e in raw["effects"]["catalog"] if e["id"] == eid)


def _actor(raw: dict[str, Any], aid: str) -> dict[str, Any]:
    return next(a for a in raw["fixtures"]["actors"] if a["id"] == aid)


def _pack_divergences(s: Subject) -> Iterator[tuple[str, str, str, Pack | str]]:
    used = {e for t in s.model.transitions for e in t.required_effects}
    for effect in s.pack.effects.catalog:
        if effect.id not in used:
            continue
        ref = f"effect:{effect.id}"
        if effect.kind == "audit":
            yield "effect-kind-changed", ref, f"{effect.id} is queued as a notification, not audited", _pack_change(
                s, lambda raw, v=effect.id: _effect(raw, v).update(kind="notification", recipient="someone"))
        else:
            yield "effect-kind-changed", ref, f"{effect.id} is audited, not queued", _pack_change(
                s, lambda raw, v=effect.id: (_effect(raw, v).update(kind="audit"), _effect(raw, v).pop("recipient", None)))
            yield "recipient-changed", ref, f"{effect.id} goes to someone other than {effect.recipient}", _pack_change(
                s, lambda raw, v=effect.id: _effect(raw, v).update(recipient=f"not-{_effect(raw, v).get('recipient') or 'anyone'}"))
    needs_assignment = {t.role for t in s.model.transitions if "actor_assigned" in t.guards}
    for actor in sorted(s.pack.fixtures.actors, key=lambda a: a.id):
        ref = f"actor:{actor.id}"
        yield "actor-active-flipped", ref, f"{actor.id} is {'revoked' if actor.active else 'active'}", _pack_change(
            s, lambda raw, v=actor.id: _actor(raw, v).update(active=not _actor(raw, v)["active"]))
        if not actor.active or actor.role not in needs_assignment:
            continue  # assignment is read only for an active actor taking a transition that needs it
        yield "actor-assigned-flipped", ref, f"{actor.id} is {'not ' if actor.assigned else ''}assigned", _pack_change(
            s, lambda raw, v=actor.id: _actor(raw, v).update(assigned=not _actor(raw, v)["assigned"]))
    for law in s.pack.laws:
        if isinstance(law, DistinctActors):
            yield "separation-law-dropped", f"law:{law.id}", f"one actor may take {' and '.join(law.actions)}", _pack_change(
                s, lambda raw, v=law.id: raw.__setitem__("laws", [x for x in raw["laws"] if x["id"] != v]))


def _data_change(data: DataModel, change: Callable[[dict[str, Any]], None]) -> DataModel | str:
    raw = data.model_dump(mode="json")
    change(raw)
    try:
        return DataModel.model_validate(raw)
    except ValidationError as invalid:
        return f"INVALID_DATA: {invalid.errors()[0]['msg']}"


def _record_attribute(raw: dict[str, Any], name: str) -> dict[str, Any]:
    entity = next(e for e in raw["entities"] if e["name"] == raw["record"])
    return next(a for a in entity["attributes"] if a["name"] == name)


def _data_divergences(s: Subject) -> Iterator[tuple[str, str, str, DataModel | str]]:
    data = s.data
    if data is None:
        return
    entity = data.entity(data.record)
    for a in entity.attributes:
        ref, name = f"attribute:{data.record}.{a.name}", a.name
        yield "attribute-required-flipped", ref, f"{a.name} is {'optional' if a.required else 'required'}", _data_change(
            data, lambda raw, name=name: _record_attribute(raw, name).update(required=not _record_attribute(raw, name).get("required", False)))
        yield "attribute-dropped", ref, f"{a.name} is not a field", _data_change(
            data, lambda raw, name=name: next(e for e in raw["entities"] if e["name"] == raw["record"])["attributes"].remove(
                _record_attribute(raw, name)))
        retyped = "number" if a.type != "number" else "text"
        yield "attribute-retyped", ref, f"{a.name} holds a {retyped}", _data_change(
            data, lambda raw, name=name, v=retyped: (_record_attribute(raw, name).update(type=v),
                                          _record_attribute(raw, name).pop("choices", None),
                                          _record_attribute(raw, name).pop("max_length", None)))
        if a.type == "text":
            yield "attribute-length-changed", ref, f"{a.name} holds one character fewer", _data_change(
                data, lambda raw, name=name, a=a: _record_attribute(raw, name).update(max_length=a.max_length - 1))
        if a.type == "choice" and len(a.choices) > 1:
            yield "attribute-choice-dropped", ref, f"{a.name} no longer offers {a.choices[-1]}", _data_change(
                data, lambda raw, name=name, a=a: _record_attribute(raw, name).__setitem__("choices", list(a.choices[:-1])))
    for n, association in enumerate(data.associations):
        if association.built and data.record in (association.source, association.target):
            ref = f"association:{association.source}-{association.target}"
            yield "association-dropped", ref, f"{association.source} no longer refers to {association.target}", \
                _data_change(data, lambda raw, i=n: raw["associations"].pop(i))
            yield "association-unbuilt", ref, f"{association.source} -> {association.target} is drawn but not stored", \
                _data_change(data, lambda raw, i=n: raw["associations"][i].pop("built"))
            many = "0..1" if association.target_multiplicity == "1" else "1"
            yield "association-multiplicity-changed", ref, f"a record refers to {many} {association.target}", \
                _data_change(data, lambda raw, i=n, v=many: raw["associations"][i].update(target_multiplicity=v))


def divergences(s: Subject) -> list[Divergence]:
    found: list[Divergence] = []
    for kind, ref, text, model in _model_divergences(s):
        found.append(Divergence(kind, ref, text, model=model, refused=model) if isinstance(model, str)
                     else Divergence(kind, ref, text, model=model))
    for kind, ref, text, pack in _pack_divergences(s):
        found.append(Divergence(kind, ref, text, refused=pack) if isinstance(pack, str) else Divergence(kind, ref, text, pack=pack))
    for kind, ref, text, data in _data_divergences(s):
        found.append(Divergence(kind, ref, text, refused=data) if isinstance(data, str) else Divergence(kind, ref, text, data=data))
    for name, (path, before, after) in CODE.items():
        if APPLIES.get(name, lambda _: True)(s):
            found.append(Divergence("code", f"code:{name}", name, code=(path, before, after)))
    return found


def _values(s: Subject) -> bool:
    return any(t.conditions for t in s.model.transitions)


def _separation(s: Subject) -> bool:
    actions = {t.action for t in s.model.transitions}
    return any(isinstance(law, DistinctActors) and len(set(law.actions) & actions) > 1 for law in s.pack.laws)


def _notifies(s: Subject) -> bool:
    return any(e.kind != "audit" for t in s.model.transitions for e in map(s.pack.effect, t.required_effects) if e)


def _several_sources(s: Subject) -> bool:
    return any(len(s.model.sources(t.action)) > 1 for t in s.model.transitions)


# Where a fault can show at all: a fault in code a subject never reaches is NOT_APPLICABLE to it, not missed.
APPLIES: dict[str, Callable[[Subject], bool]] = {
    "notification not queued": _notifies, "notification sent to nobody": _notifies, "notification names no record": _notifies,
    "record values not checked on create": lambda s: s.data is not None, "record values not stored": lambda s: s.data is not None,
    "created record not stamped with its data model": lambda s: s.data is not None,
    "HTTP drops record values": lambda s: s.data is not None,
    "guards read no record values": _values, "offered actions ignore value guards": _values,
    "who acted is not remembered": _separation, "offered actions ignore separation of duties": _separation,
    "anyone may start a record": lambda s: bool(s.model.initiators),
    "rule table shows one source per action": _several_sources,
}

# Seeded faults in the app's own code. Each changes what the app does in a way the model does not allow.
CODE: dict[str, tuple[str, str, str]] = {
    "operation not recorded (no idempotency)": (
        "app/service.py", 'self.db.execute("INSERT INTO operations VALUES(?,?,?)", (operation_id, binding, canonical(result)))',
        "return None"),
    "audit entry not written": (
        "app/service.py", 'self.db.execute("INSERT INTO audit(kind, body) VALUES(?,?)", (kind, canonical(body)))', "return None"),
    "notification not queued": (
        "app/service.py", 'self.db.execute("INSERT INTO outbox VALUES(?,?,?,?)", (operation_id + ":" + effect, self.record_id, effect, recipient))',
        "return None"),
    "notification sent to nobody": (
        "app/service.py", '(operation_id + ":" + effect, self.record_id, effect, recipient))',
        '(operation_id + ":" + effect, self.record_id, effect, ""))'),
    "notification names no record": (
        "app/service.py", '(operation_id + ":" + effect, self.record_id, effect, recipient))',
        '(operation_id + ":" + effect, case_id, effect, recipient))'),
    "record values not checked on create": (
        "app/service.py", "values = check_record(DATA, fields or {}, self._exists)", "values = dict(fields or {})"),
    "record values not stored": (
        "app/service.py", "(title, actor_id, canonical(values), DATA_DIGEST, item[\"id\"])", "(title, actor_id, '{}', DATA_DIGEST, item[\"id\"])"),
    "created record not stamped with its data model": (
        "app/service.py", "(title, actor_id, canonical(values), DATA_DIGEST, item[\"id\"])", "(title, actor_id, canonical(values), '', item[\"id\"])"),
    "guards read no record values": ("app/service.py", 'return json.loads(row["fields"]) if row else {}', "return {}"),
    "who acted is not remembered": (
        "app/service.py", 'self.db.execute("INSERT INTO acts(record_id, action, actor_id) VALUES(?,?,?)", (instance_id, action, actor_id))',
        "return None"),
    "anyone may start a record": (
        "app/service.py", 'initialise(session, CASE, MODEL, pack=PACK, role=actor["role"])', "initialise(session, CASE, MODEL, pack=PACK)"),
    "revoked actors may start a record": (
        "app/service.py", 'if not actor["active"]:\n            raise DomainError("ACTOR_REVOKED", "Actor is not active")',
        'if False:\n            raise DomainError("ACTOR_REVOKED", "Actor is not active")'),
    "stale data not refused": ("app/service.py", 'if row is not None and row["data_digest"] != DATA_DIGEST:', "if False:"),
    "stale records shown as current": (
        "app/service.py", 'record["current_model"] = record["model_hash"] == MODEL.semantic_hash and record["data_digest"] == DATA_DIGEST',
        'record["current_model"] = True'),
    "offered actions ignore value guards": ("app/service.py", "            check_guards(t, values or {})\n", ""),
    "offered actions ignore the actor": (
        "app/service.py", "check_actor(ACTORS[actor_id], t, None)  # type: ignore[arg-type]  # the command is not read by the check",
        "pass"),
    "offered actions ignore separation of duties": (
        "app/service.py", "            check_separation(separations(PACK, MODEL, t.action), t.action, actor_id, acts or [])\n", ""),
    "history shows every record's steps": ('app/service.py', 'if body.get("instance_id") == record_id:', "if True:"),
    "HTTP drops the expected version": (
        "app/server.py", 'str(body.get("action", "")),\n                                                       version,',
        'str(body.get("action", "")),\n                                                       0,'),
    "HTTP drops the operation id": (
        "app/server.py", 'str(body.get("operation_id", ""))[:100] or "missing"', '"missing"'),
    "HTTP refusals answered as success": ("app/server.py", 'self._json(status, {"code": refused.code, "message": refused.message})',
                                          'self._json(200, {"code": refused.code, "message": refused.message})'),
    "HTTP drops record values": ("app/server.py", 'fields = body.get("fields", {})\n                    if not isinstance(fields, dict):\n                        raise Refused("BAD_REQUEST", "fields must be a JSON object")\n                    return self._json(201, service.create(',
                                 'fields = {}\n                    if not isinstance(fields, dict):\n                        raise Refused("BAD_REQUEST", "fields must be a JSON object")\n                    return self._json(201, service.create('),
    "rule table shows one source per action": (
        "app/server.py", '{"from": ", ".join(MODEL.sources(t.action)), "to"', '{"from": t.from_state, "to"'),
}


# ---------------------------------------------------------------------------------------------------- builds


def _assemble(pack: Pack, model: Workflow, data: DataModel | None) -> tuple[dict[str, str], dict[str, Any]]:
    """The app's files with default screens (screens are layout, not rules) and no build identity yet."""
    screens = default_screens(pack, model, data)
    generated, _ = generate(pack, model, data, screens)
    files = dict(STATIC) | {"tests/__init__.py": ""} | generated
    return files, json.loads(generated["tests/oracle.json"]) | {"_screens_digest": screens.digest}


def _seal(files: dict[str, str]) -> dict[str, str]:
    payload = {k: v for k, v in files.items() if k != SUBJECT_FILE}
    subject = build_subject(payload, implementation_digest=IMPLEMENTATION, template_paths=STATIC)
    return payload | {SUBJECT_FILE: canonical(subject) + "\n"}


def _divergent(s: Subject, d: Divergence, reviewed: dict[str, Any]) -> dict[str, str]:
    """The divergent app with the reviewed oracle, its identity fields re-pointed at this app."""
    pack, model, data = d.pack or s.pack, d.model or s.model, d.data or s.data
    files, own = _assemble(pack, model, data)
    oracle = {k: v for k, v in reviewed.items() if not k.startswith("_")} | {
        "model_hash": own["model_hash"], "screens_digest": own["_screens_digest"]}
    if "data_digest" in own:
        oracle["data_digest"] = own["data_digest"]
    files["tests/oracle.json"] = canonical(oracle) + "\n"
    if d.code is not None:
        path, before, after = d.code
        if before not in files[path]:
            raise LookupError(f"seeded fault {d.text!r} no longer matches {path}")
        files[path] = files[path].replace(before, after, 1)
    return _seal(files)


RESULT = re.compile(r"^(test_\w+) \([\w.]+\)(?: \(.*\))? \.\.\. (ok|FAIL|ERROR|skipped.*)$", re.M)
FAILED = re.compile(r"^(?:FAIL|ERROR): (test_\w+|setUpClass) ", re.M)


def run_suite(files: dict[str, str]) -> tuple[int, list[str], str]:
    """Write the app and run its generated tests in a fresh process, as `eija build` does."""
    env = {k: v for k, v in os.environ.items() if k.upper() in {"SYSTEMROOT", "WINDIR"}}
    with TemporaryDirectory(prefix="eija-divergence-") as tmp:
        out = Path(tmp)
        for relative, text in files.items():
            (out / relative).parent.mkdir(parents=True, exist_ok=True)
            (out / relative).write_text(text, encoding="utf-8")
        run = subprocess.run([sys.executable, "-I", "-B", "-m", "unittest", "discover", "-s", "tests", "-t", ".", "-v"],
                             cwd=out, env=env, capture_output=True, text=True, timeout=TIMEOUT_S, check=False)
    text = run.stderr + run.stdout
    return run.returncode, sorted(set(FAILED.findall(text))), text


def judge(s: Subject, d: Divergence, reviewed: dict[str, Any]) -> Outcome:
    if d.refused is not None:
        return Outcome(d, "REFUSED", detail=d.refused)
    try:
        files = _divergent(s, d, reviewed)
    except DomainError as refused:
        return Outcome(d, "REFUSED", detail=refused.code)
    code, failed, text = run_suite(files)
    if "setUpClass" in failed:
        return Outcome(d, "HARNESS_ERROR", failed, text[-2000:])
    if code == 0:
        return Outcome(d, "EQUIVALENT" if d.kind in EQUIVALENT else "MISSED")
    return Outcome(d, "CAUGHT", failed)


def law_coverage(s: Subject, outcomes: list[Outcome]) -> list[dict[str, Any]]:
    """For each law: the model divergences that break it, and whether every one was caught or refused."""
    rows = {law.id: {"law": law.id, "kind": law.kind, "broken_by": 0, "caught": 0, "missed": []} for law in s.pack.laws}
    for o in outcomes:
        d = o.divergence
        if not isinstance(d.model, Workflow):
            continue
        try:
            report = prove_laws(s.pack, d.model)
        except DomainError:
            continue
        for verdict in report["laws"]:
            if verdict["status"] == "BROKEN" and verdict["id"] in rows:
                row = rows[verdict["id"]]
                row["broken_by"] += 1
                if o.status in ("CAUGHT", "REFUSED"):
                    row["caught"] += 1
                else:
                    row["missed"].append(f"{d.ref}: {d.text}")
    return list(rows.values())


def check(subject: Subject, workers: int) -> dict[str, Any]:
    _, reviewed = _assemble(subject.pack, subject.model, subject.data)
    # The control: the reviewed app, resealed the same way, must pass its own suite. Otherwise every divergence of
    # this subject would look caught, and none of them is evidence.
    code, failed, _ = run_suite(_divergent(subject, Divergence("control", "control", "no divergence"), reviewed))
    if code != 0:
        return {"subject": subject.name, "counts": {"HARNESS_ERROR": 1}, "by_kind": {}, "equivalent": [], "laws": [],
                "caught_by": {}, "missed": [{"kind": "control", "ref": "control",
                                             "text": f"the reviewed app fails its own suite: {failed}"}]}
    plan = divergences(subject)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        outcomes = list(pool.map(lambda d: judge(subject, d, reviewed), plan))
    counts = Counter(o.status for o in outcomes)
    return {"subject": subject.name, "counts": dict(sorted(counts.items())),
            "by_kind": {kind: dict(Counter(o.status for o in outcomes if o.divergence.kind == kind))
                        for kind in sorted({o.divergence.kind for o in outcomes})},
            "missed": [{"kind": o.divergence.kind, "ref": o.divergence.ref, "text": o.divergence.text}
                       for o in outcomes if o.status in ("MISSED", "HARNESS_ERROR")],
            "equivalent": sorted({o.divergence.kind for o in outcomes if o.status == "EQUIVALENT"}),
            "laws": law_coverage(subject, outcomes),
            "caught_by": dict(sorted(Counter(t for o in outcomes for t in o.failed).items()))}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--pack", action="append", help="Only these subjects (pack directory names or variant names)")
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "conformance" / "divergence.json")
    parser.add_argument("--core", action="store_true", help="Only library-loan and the two feature variants (the full tier)")
    parser.add_argument("--workers", type=int, default=max(1, min(8, os.cpu_count() or 1)))
    args = parser.parse_args(argv)
    chosen = set(args.pack or ()) | (set(CORE) if args.core else set())
    subjects = [s for s in shipped() + variants() if not chosen or s.name in chosen]
    results = []
    for subject in subjects:
        result = check(subject, args.workers)
        results.append(result)
        laws_missed = sum(len(r["missed"]) for r in result["laws"])
        sys.stdout.write(f"{subject.name}: {result['counts']}; laws with a missed break: {laws_missed}\n")
        sys.stdout.flush()
    ok = all(not r["missed"] and not any(law["missed"] for law in r["laws"]) for r in results)
    report = {"format": FORMAT, "status": "PASS" if ok else "FAIL", "equivalent": EQUIVALENT, "subjects": results}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    sys.stdout.write(f"{report['status']}: see {args.out}\n")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
