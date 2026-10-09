"""Start a new system (ADR-0185): the pack documents for a system started from a sketch or copied from a template.

A system is a pack: `pack.json`, with `data.json`, `screens.json` and `scenarios.json` beside it when it has them. This module only
writes documents; the kernel's own pack check (`parse_pack`) decides whether they are a system at all, and the
caller saves them. A sketch is one transition per line in the state machine's own label notation,
`From -> To : Action [Role]`, so what you type is what the diagram draws. Nothing here infers laws, effects
beyond one audit entry per action, or meanings the person did not write.
"""
from __future__ import annotations

import copy
import re
from typing import Any

from eija_studio.domain.data import parse_data
from eija_studio.domain.models import BASE_GUARDS, DomainError
from eija_studio.domain.pack import Pack, PackError, parse_pack
from eija_studio.domain.scenarios import parse_scenarios
from eija_studio.domain.screens import parse_screens

NAME = r"[A-Za-z][A-Za-z0-9_]{0,39}"  # states, actions and roles: names the built app's code can use as they are
LINE = re.compile(rf"^\s*({NAME})\s*->\s*({NAME})\s*:\s*({NAME})\s*\[\s*({NAME})\s*\]\s*$")
LIST = re.compile(r"^\s*(actions|roles)\s*:\s*(.*)$", re.IGNORECASE)
RECORD = re.compile(r"^[A-Z][A-Za-z0-9]{0,39}$")
MAX_LINES = 64
UNSUPPORTED = "unsupported"
SKETCH_HELP = "One transition per line, as the diagram labels it: From -> To : Action [Role]"


def system_id(name: str, taken: set[str]) -> str:
    """A pack id for a new system called `name`, unlike every id in `taken`."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    slug = (slug if slug[:1].isalpha() else "system-" + slug).strip("-")[:36].strip("-") or "system"
    found, n = slug, 2
    while found in taken:
        found, n = f"{slug}-{n}", n + 1
    return found


def _names(text: str) -> list[str]:
    return [part.strip() for part in text.split(",") if part.strip()]


def _list_line(n: int, kind: str, text: str, extra: dict[str, list[str]]) -> list[str]:
    """An `actions:` or `roles:` line: names to declare without a transition yet."""
    names = _names(text)
    extra[kind.lower()] += [x for x in names if re.fullmatch(NAME, x)]
    return [f"line {n}: {x!r} is not a name (letters, digits and _)" for x in names if not re.fullmatch(NAME, x)]


def _transition_line(n: int, line: str, used: dict[str, int], transitions: list[tuple[str, ...]]) -> list[str]:
    """A `From -> To : Action [Role]` line."""
    match = LINE.match(line)
    if not match:
        return [f"line {n}: write it as {SKETCH_HELP.split(': ', 1)[1]}"]
    action = match.group(3)
    if action in used:
        return [f"line {n}: action {action} already labels line {used[action]}; each action labels one transition"]
    used[action] = n
    transitions.append(match.groups())
    return []


def parse_sketch(text: str) -> dict[str, Any]:
    """The transitions, extra actions and extra roles of a sketch, or `PackError` naming each bad line."""
    lines = text.splitlines()
    if len(lines) > MAX_LINES:
        raise PackError([f"sketch: at most {MAX_LINES} lines"])
    transitions: list[tuple[str, ...]] = []
    extra: dict[str, list[str]] = {"actions": [], "roles": []}
    used: dict[str, int] = {}
    problems: list[str] = []
    for n, line in enumerate(lines, 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        found = LIST.match(line)
        problems += _list_line(n, found.group(1), found.group(2), extra) if found else _transition_line(n, line, used, transitions)
    if not transitions and not problems:
        problems.append(f"sketch: {SKETCH_HELP}")
    if problems:
        raise PackError(problems)
    return {"transitions": transitions, **extra}


def _transition_id(action: str, taken: set[str]) -> str:
    base = "TR-" + re.sub(r"[^A-Z0-9_]", "", action.upper())
    found, n = base, 2
    while found in taken:
        found, n = f"{base}-{n}", n + 1
    taken.add(found)
    return found


def _role_actor(role: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", role.lower()).strip("-") or "actor"


def _fixtures(roles: list[str], states: list[str]) -> dict[str, Any]:
    """One active, assigned user per role, one revoked user of the first role so a simulation meets a refusal, and an
    offline proposer that says this system has no modelled change requests."""
    actors = [{"id": f"{_role_actor(role)}-1", "role": role, "active": True, "assigned": True} for role in roles]
    return {"actors": [*actors, {"id": f"{_role_actor(roles[0])}-revoked", "role": roles[0], "active": False, "assigned": True}],
            "proposals": {"summary": "Offline: this system has no modelled change requests; no model inference was used.",
                          "rules": [], "fallback": [{"interpretation": UNSUPPORTED, "explanation": "This system has no modelled change requests yet."}],
                          "unknowns": []},
            "demo_request": f"Add a review step before {states[-1]}."}


def sketch_documents(name: str, record: str, sketch: str, pack_id: str) -> dict[str, dict[str, Any]]:
    """`pack.json` and `data.json` for a system started from a sketch, checked by the kernel's pack check."""
    if not RECORD.match(record):
        raise PackError([f"record: {record!r} is not a UML class name (UpperCamelCase, letters and digits)"])
    parsed = parse_sketch(sketch)
    states = list(dict.fromkeys(s for t in parsed["transitions"] for s in (t[0], t[1])))
    roles = list(dict.fromkeys([t[3] for t in parsed["transitions"]] + parsed["roles"]))
    actions = list(dict.fromkeys([t[2] for t in parsed["transitions"]] + parsed["actions"]))
    ids: set[str] = set()
    transitions = [{"id": _transition_id(action, ids), "action": action, "from_state": source, "to_state": target,
                    "role": role, "guards": list(BASE_GUARDS), "required_effects": [f"Audit:{action}"], "forbidden_effects": []}
                   for source, target, action, role in parsed["transitions"]]
    pack = {
        "schema_version": "eija.pack.v1",
        "pack": {"id": pack_id, "name": name, "version": "0.1.0",
                 "description": f"Started in PlayIDE from a sketch: one {record} moving through {len(states)} states."},
        "model": {"schema_version": "eija.workflow.v1", "id": pack_id, "initial_state": parsed["transitions"][0][0],
                  "states": states, "transitions": transitions},
        "roles": [{"id": role} for role in roles],
        "actions": [{"id": action, "guards": list(BASE_GUARDS), "required_effects": [f"Audit:{action}"]} for action in actions],
        "effects": {"catalog": [{"id": f"Audit:{action}", "kind": "audit"} for action in actions], "forbidden": []},
        "laws": [],
        "meanings": [{"id": UNSUPPORTED, "label": "Outside the modelled scope", "supported": False,
                      "consequences": ["This system has no modelled change requests yet; change it on the diagram."]}],
        "language": {"terms": []},
        "fixtures": _fixtures(roles, states),
        "verifiers": [{"kind": "runtime_matrix", "mode": "kernel"}],
        "journey": {"questions": []},
    }
    data = {"schema_version": "eija.data.v1", "id": pack_id, "record": record,
            "entities": [{"name": record, "description": f"One {record}; it moves through the state machine.",
                          "attributes": [{"name": "title", "type": "text", "required": True, "max_length": 200}]}]}
    return _checked({"pack.json": pack, "data.json": data})


def template_documents(template: Pack, documents: dict[str, dict[str, Any]], name: str, pack_id: str) -> dict[str, dict[str, Any]]:
    """A copy of a template's documents as a new system: new id and name, the same model, rules, laws, screens and
    test cases (`scenarios.json`).

    What belonged only to the template is dropped: its language terms' `repo://` bindings, and any claim of a
    hand-written formal model, which was written for the template's id and is not this system's."""
    pack = copy.deepcopy(documents["pack.json"])
    pack["pack"] = {"id": pack_id, "name": name, "version": "0.1.0",
                    "description": f"Started in PlayIDE from the {template.pack.name} template."}
    pack["model"]["id"] = pack_id
    for term in pack.get("language", {}).get("terms", []):
        term["binds"] = []
    pack["verifiers"] = [v if v.get("mode") != "hand_encoded" else
                         {"kind": v["kind"], "mode": "not_run",
                          "reason": f"The hand-written formal model belongs to the {template.pack.name} pack, not this copy."}
                         for v in pack.get("verifiers", [])]
    copied = {"pack.json": pack}
    for file in ("data.json", "screens.json", "scenarios.json"):
        if file in documents:
            copied[file] = copy.deepcopy(documents[file]) | {"id": pack_id}
    return _checked(copied)


def _checked(documents: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """The documents, if the kernel's checks accept them; `PackError` with every problem otherwise."""
    pack = parse_pack(documents["pack.json"])
    try:
        if "data.json" in documents:
            parse_data(documents["data.json"], pack.id)
        if "screens.json" in documents:
            parse_screens(documents["screens.json"], pack.id)
        if "scenarios.json" in documents:
            parse_scenarios(documents["scenarios.json"], pack.id)
    except DomainError as error:
        raise PackError([error.message]) from None
    return documents


def summary(documents: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """What the new system has, for the form to say before it is created."""
    pack = parse_pack(documents["pack.json"])
    return {"id": pack.id, "name": pack.pack.name, "initial": pack.model.initial_state, "states": list(pack.model.states),
            "transitions": len(pack.model.transitions), "roles": [r.id for r in pack.roles],
            "actions": [a.id for a in pack.actions], "record": documents.get("data.json", {}).get("record")}
