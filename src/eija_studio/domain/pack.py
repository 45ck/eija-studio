"""Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

A pack is data, never code: the baseline workflow (``model``), its roles, the declared action catalog
(guards and required effects per action), typed effects, laws, the meanings an owner may select, the
language terms with ``repo://`` bindings, offline fixtures (actors, proposals, demo request), the verifiers
that apply, and the review journey. Generic code reads a pack; it never names a pack's states, roles or actions.

Loading is total: any defect (unreadable file, bad JSON, wrong shape, a reference to an undeclared state, role,
action or effect) becomes ``PackError`` (code ``PACK_INVALID``) with SORTED diagnostics. It never crashes.
"""
from __future__ import annotations

import json
import os
import re
import tomllib
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, ValidationError

from .laws import Law
from .models import MEANING_ID, Alternative, Contract, DomainError, Guard, Workflow, fingerprint
from .transactions import AddState, RemoveState, Transaction

PACK_SCHEMA = "eija.pack.v1"
PACK_ID = r"^[a-z][a-z0-9-]{0,39}$"
REPO_URI = r"^repo://[A-Za-z0-9_./#:@-]{1,300}$"
PACK_FILE = "pack.json"
DEFAULT_FILE = "default.json"
ENV_PACK = "EIJA_PACK"
def _source_checkout(package: Path) -> bool:
    """Recognize the canonical source layout without requiring Git or executing project code."""
    if (package.parent.name, package.name) != ("src", "eija_studio"):
        return False
    try:
        with (package.parents[1] / "pyproject.toml").open("rb") as metadata:
            project = tomllib.load(metadata).get("project")
    except (OSError, UnicodeError, tomllib.TOMLDecodeError):
        return False
    return isinstance(project, dict) and project.get("name") == "eija-studio"


def _packs_root(package: Path) -> Path:
    """Only a recognized source checkout may load authored packs outside package resources."""
    bundled = package / "resources" / "packs"
    return bundled if bundled.exists() or not _source_checkout(package) else package.parents[1] / "packs"


PACKS_ROOT = _packs_root(Path(__file__).resolve().parents[1])


class PackInfo(Contract):
    id: str = Field(pattern=PACK_ID)
    name: str = Field(min_length=1, max_length=120)
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    description: str = Field(default="", max_length=2000)


class Role(Contract):
    id: str = Field(min_length=1, max_length=60)
    description: str = Field(default="", max_length=400)


class ActionSpec(Contract):
    """The declared guards and required effects of one action; the policy holds every transition to them."""
    id: str = Field(min_length=1, max_length=60)
    guards: tuple[Guard, ...] = Field(min_length=1)
    required_effects: tuple[str, ...] = ()


class Effect(Contract):
    """A typed effect. ``audit`` is written to the audit log, ``notification`` to the outbox for ``recipient``."""
    id: str = Field(min_length=1, max_length=80)
    kind: Literal["audit", "notification"]
    recipient: str | None = Field(default=None, max_length=60)


class Effects(Contract):
    catalog: tuple[Effect, ...] = ()
    forbidden: tuple[str, ...] = ()


class Meaning(Contract):
    """One interpretation of a request. A supported meaning's transactions produce the candidate; an unsupported
    one's transactions (if any) describe what it WOULD do, for explanation only, never as a candidate."""
    id: str = Field(pattern=MEANING_ID)
    label: str = Field(min_length=1, max_length=200)
    supported: bool
    consequences: tuple[str, ...] = Field(min_length=1)
    transactions: tuple[Transaction, ...] = ()


class Term(Contract):
    id: str = Field(pattern=r"^[a-z][a-z0-9-]{0,63}$")
    label: str = Field(min_length=1, max_length=120)
    definition: str = Field(default="", max_length=2000)
    binds: tuple[str, ...] = ()
    refs: tuple[str, ...] = ()  # model elements this term names: "state:<id>", "transition:<id>", "role:<id>", "law:<id>"


class Language(Contract):
    terms: tuple[Term, ...] = ()


class Actor(Contract):
    id: str = Field(min_length=1, max_length=80)
    role: str = Field(min_length=1, max_length=60)
    active: bool
    assigned: bool


class ProposalRule(Contract):
    """Offline fixture: when the lower-cased request contains every ``all`` word and at least one ``any`` word."""
    all: tuple[str, ...] = ()
    any: tuple[str, ...] = ()
    alternatives: tuple[Alternative, ...] = Field(min_length=1, max_length=4)


class Proposals(Contract):
    summary: str = Field(min_length=1, max_length=1600)
    rules: tuple[ProposalRule, ...] = ()
    fallback: tuple[Alternative, ...] = Field(min_length=1, max_length=4)
    unknowns: tuple[str, ...] = Field(default=(), max_length=10)


class Fixtures(Contract):
    actors: tuple[Actor, ...] = Field(min_length=1)
    proposals: Proposals
    demo_request: str = Field(min_length=1, max_length=6000)


class Verifier(Contract):
    """An evidence kind that applies to this pack (``kind`` is the evidence kind's name). ``hand_encoded`` marks a
    hand-written formal model of the pack; ``generated`` a model generated from the pack's laws; ``not_run`` records
    that the kind is deliberately not produced for this pack, with the reason. Only ``kernel`` and ``hand_encoded``
    kinds read the checkout's committed formal reports; every other kind is NOT_RUN in the review packet, with the reason."""
    kind: str = Field(pattern=r"^[a-z][a-z0-9_]{0,39}$")
    mode: Literal["kernel", "hand_encoded", "generated", "not_run"]
    reason: str = Field(default="", max_length=400)


class Question(Contract):
    """A meaning-check question for the owner. The expected answer is literal, or read from a transition field."""
    id: str = Field(pattern=r"^[a-z][a-z0-9_]{0,39}$")
    question: str = Field(min_length=1, max_length=400)
    expected: str | None = Field(default=None, max_length=120)
    expected_from: tuple[str, Literal["from_state", "to_state", "role"]] | None = None


class Journey(Contract):
    questions: tuple[Question, ...] = ()


class Pack(Contract):
    schema_version: Literal["eija.pack.v1"] = "eija.pack.v1"
    pack: PackInfo
    model: Workflow
    roles: tuple[Role, ...] = Field(min_length=1)
    actions: tuple[ActionSpec, ...] = Field(min_length=1)
    effects: Effects
    laws: tuple[Law, ...] = ()
    meanings: tuple[Meaning, ...] = Field(min_length=1)
    language: Language = Language()
    fixtures: Fixtures
    verifiers: tuple[Verifier, ...] = ()
    journey: Journey = Journey()

    @property
    def id(self) -> str:
        return self.pack.id

    @property
    def digest(self) -> str:
        return fingerprint(self)

    def action(self, name: str) -> ActionSpec | None:
        return next((a for a in self.actions if a.id == name), None)

    def verifier(self, kind: str) -> Verifier | None:
        return next((v for v in self.verifiers if v.kind == kind), None)

    def meaning(self, meaning_id: str) -> Meaning | None:
        return next((m for m in self.meanings if m.id == meaning_id), None)

    def effect(self, effect_id: str) -> Effect | None:
        return next((e for e in self.effects.catalog if e.id == effect_id), None)


def state_sets(pack: Pack) -> tuple[frozenset[str], ...]:
    """The state sets a workflow of this pack can have: the baseline's, and the baseline's after each supported
    meaning (states its transactions add or remove). Used to bound evidence whose model is not at hand."""
    base = frozenset(pack.model.states)
    sets = [base]
    for meaning in pack.meanings:
        if meaning.supported:
            added = {tx.state for tx in meaning.transactions if isinstance(tx, AddState)}
            removed = {tx.state for tx in meaning.transactions if isinstance(tx, RemoveState)}
            sets.append(frozenset((base | added) - removed))
    return tuple(dict.fromkeys(sets))


def ui_key(pack_id: str, kind: str, element: str) -> str:
    """The derived UI/UML key of a pack element: ``data-eija-id="<pack>.<kind>.<id>"``."""
    return f"{pack_id}.{kind}.{element}"


class PackError(DomainError):
    """A pack that cannot be used. ``diagnostics`` is sorted and never empty."""
    def __init__(self, diagnostics: list[str]):
        self.diagnostics = tuple(sorted(set(diagnostics))) or ("unknown pack defect",)
        super().__init__("PACK_INVALID", "; ".join(self.diagnostics[:5]))


# ---- cross-references (what JSON Schema cannot state) ------------------------------------------------------

def _known_states(pack: Pack) -> set[str]:
    added = {tx.state for m in pack.meanings for tx in m.transactions if isinstance(tx, AddState)}
    return set(pack.model.states) | added


def _law_refs(law: Any) -> list[tuple[str, str]]:
    """(category, name) pairs a law refers to."""
    refs: list[tuple[str, str]] = []
    for field, category in (("action", "action"), ("role", "role"), ("state", "state"), ("via", "state"), ("initial_state", "state")):
        if isinstance(getattr(law, field, None), str):
            refs.append((category, getattr(law, field)))
    for field, category in (("actions", "action"), ("states", "state")):
        refs += [(category, x) for x in getattr(law, field, ())]
    refs += [("effect", x) for x in getattr(law, "effects", ())]
    return refs


def _duplicates(label: str, ids: list[str]) -> list[str]:
    return [f"{label}: duplicate id {x!r}" for x in sorted({x for x in ids if ids.count(x) > 1})]


def _model_problems(pack: Pack) -> list[str]:
    roles, actions = {r.id for r in pack.roles}, {a.id for a in pack.actions}
    found = [f"model.transitions[{t.id}]: action {t.action!r} is not declared in actions" for t in pack.model.transitions if t.action not in actions]
    found += [f"model.transitions[{t.id}]: role {t.role!r} is not declared in roles" for t in pack.model.transitions if t.role not in roles]
    return found + [f"fixtures.actors[{a.id}]: role {a.role!r} is not declared in roles" for a in pack.fixtures.actors if a.role not in roles]


def _effect_problems(pack: Pack) -> list[str]:
    effects = {e.id for e in pack.effects.catalog}
    found = [f"actions[{a.id}]: effect {e!r} is not in effects.catalog" for a in pack.actions for e in a.required_effects if e not in effects]
    found += [f"effects.forbidden: {e!r} is also a catalog effect" for e in pack.effects.forbidden if e in effects]
    return found + _recipient_problems(pack) + [f"actions[{a.id}]: the runtime matrix observes at most one {kind} effect per action"
                    for a in pack.actions for kind in ("audit", "notification") if _count(pack, a, kind) > 1]


def _recipient_problems(pack: Pack) -> list[str]:
    return [f"effects.catalog[{e.id}]: a notification needs a recipient" for e in pack.effects.catalog if e.kind == "notification" and not e.recipient]


def _count(pack: Pack, action: ActionSpec, kind: str) -> int:
    return sum(1 for e in action.required_effects if (found := pack.effect(e)) is not None and found.kind == kind)


def _law_problems(pack: Pack) -> list[str]:
    known = {"state": _known_states(pack), "role": {r.id for r in pack.roles}, "action": {a.id for a in pack.actions},
             "effect": set(pack.effects.forbidden) | {e.id for e in pack.effects.catalog}}
    return [f"laws[{law.id}]: {category} {name!r} is not declared" for law in pack.laws
            for category, name in _law_refs(law) if name not in known[category]]


def _identity_problems(pack: Pack) -> list[str]:
    found = [] if pack.model.id == pack.pack.id else [f"model.id: {pack.model.id!r} differs from pack.id {pack.pack.id!r}"]
    found += _duplicates("roles", [r.id for r in pack.roles]) + _duplicates("actions", [a.id for a in pack.actions])
    found += _duplicates("effects.catalog", [e.id for e in pack.effects.catalog]) + _duplicates("laws", [x.id for x in pack.laws])
    found += _duplicates("meanings", [m.id for m in pack.meanings]) + _duplicates("language.terms", [t.id for t in pack.language.terms])
    found += _duplicates("fixtures.actors", [a.id for a in pack.fixtures.actors])
    return found


def _fixture_problems(pack: Pack) -> list[str]:
    meanings = {m.id for m in pack.meanings}
    alternatives = [a for r in pack.fixtures.proposals.rules for a in r.alternatives] + list(pack.fixtures.proposals.fallback)
    return [f"fixtures.proposals: interpretation {a.interpretation!r} is not a meaning" for a in alternatives if a.interpretation not in meanings]


def _journey_problems(pack: Pack) -> list[str]:
    transitions = {t.id for t in pack.model.transitions}
    found = [f"journey.questions[{q.id}]: transition {q.expected_from[0]!r} is not in the model"
             for q in pack.journey.questions if q.expected_from and q.expected_from[0] not in transitions]
    found += [f"journey.questions[{q.id}]: give exactly one of expected or expected_from"
              for q in pack.journey.questions if (q.expected is None) == (q.expected_from is None)]
    return found + [f"language.terms[{t.id}]: binding {b!r} is not a repo:// URI" for t in pack.language.terms for b in t.binds
                    if not b.startswith("repo://")]


def coherence_problems(pack: Pack) -> list[str]:
    """Every cross-reference defect of a structurally valid pack, sorted."""
    return sorted(_identity_problems(pack) + _model_problems(pack) + _effect_problems(pack) + _law_problems(pack) + _fixture_problems(pack)
                  + _journey_problems(pack))


# ---- loading -----------------------------------------------------------------------------------------------

def _location(error: Any) -> str:
    return ".".join(str(part) for part in error.get("loc", ())) or "<root>"


def parse_pack(document: Any) -> Pack:
    """Validate a decoded JSON document as a pack. Raises ``PackError`` with sorted diagnostics."""
    if not isinstance(document, dict):
        raise PackError(["<root>: a pack is a JSON object"])
    try:
        pack = Pack.model_validate(document)
    except ValidationError as error:
        raise PackError([f"{_location(e)}: {e.get('msg', 'invalid')}" for e in error.errors()]) from None
    except RecursionError:
        raise PackError(["<root>: nesting too deep"]) from None
    problems = coherence_problems(pack)
    if problems:
        raise PackError(problems)
    return pack


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise PackError([f"{path.name}: cannot be read ({type(error).__name__})"]) from None


def _decode(text: str, name: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise PackError([f"{name}: invalid JSON at line {error.lineno} column {error.colno}"]) from None
    except RecursionError:
        raise PackError([f"{name}: nesting too deep"]) from None


def _read(path: Path) -> Any:
    return _decode(_read_text(path), path.name)


_LOADED: dict[tuple[str, str], Pack] = {}
_SOURCES: dict[Path, str] = {}
_DIRECTORIES: dict[tuple[str, str], Path] = {}  # where each snapshot was last read, for files beside pack.json


def load_pack(location: str | Path) -> Pack:
    """Read current file contents and retain an immutable, digest-addressed pack snapshot."""
    path = Path(location)
    path = (path / PACK_FILE if path.is_dir() else path).resolve()
    pack = _cached(_read_text(path), path.name)
    _LOADED[pack.id, pack.digest] = pack
    _SOURCES[path] = pack.id
    _DIRECTORIES[pack.id, pack.digest] = path.parent
    return pack


def derive(pack: Pack, document: Any) -> Pack:
    """A draft of `pack` held in memory (`document`, checked as `parse_pack` checks any pack), whose files beside
    `pack.json` (`data.json`, `screens.json`, `scenarios.json`) are read from where `pack` was read. A draft is never a
    loaded snapshot: `find_pack` cannot resolve it, so no change case or receipt can name it."""
    draft = parse_pack(document)
    folder = pack_directory(pack)
    if folder is not None and draft.id == pack.id:
        _DIRECTORIES[draft.id, draft.digest] = folder
    return draft


def pack_directory(pack: Pack) -> Path | None:
    """The directory this exact pack snapshot was read from, or its authored directory, so optional files beside
    `pack.json` (such as `data.json`) are read from the same place as the pack."""
    found = _DIRECTORIES.get((pack.id, pack.digest))
    if found is not None:
        return found
    authored = PACKS_ROOT / pack.id
    return authored if (authored / PACK_FILE).is_file() else None


def _refresh_sources(pack_id: str) -> None:
    paths = {path for path, identity in _SOURCES.items() if identity == pack_id}
    repository_file = PACKS_ROOT / pack_id / PACK_FILE
    if re.fullmatch(PACK_ID, pack_id) and repository_file.is_file():
        paths.add(repository_file.resolve())
    for path in sorted(paths):
        load_pack(path)


def _unique_snapshot(pack_id: str) -> Pack | None:
    if pack_id not in _SOURCES.values():
        return None
    matches = [pack for (identity, _), pack in _LOADED.items() if identity == pack_id]
    if len(matches) > 1:
        raise DomainError("PACK_IDENTITY_REQUIRED", "Multiple contents were loaded for this pack id; supply the reviewed pack digest")
    return matches[0] if matches else None


def find_pack(pack_id: str, *, digest: str | None = None) -> Pack | None:
    """Resolve a loaded snapshot by digest, or an unambiguous id after refreshing its sources.

    An id alone cannot select between different observed contents, even when their model/version matches.
    Ambiguity raises ``PACK_IDENTITY_REQUIRED`` rather than letting load order select policy or meanings.
    """
    if digest is not None and (pack := _LOADED.get((pack_id, digest))) is not None:
        return pack
    try:
        _refresh_sources(pack_id)
    except PackError:
        if any(identity == pack_id for identity in _SOURCES.values()):
            raise
        return None
    if digest is not None:
        return _LOADED.get((pack_id, digest))
    return _unique_snapshot(pack_id)


def meaning_ids(pack_id: str, *, digest: str | None = None) -> frozenset[str] | None:
    """The meaning ids of the pack a workflow belongs to, or None when no such pack can be found."""
    pack = find_pack(pack_id, digest=digest)
    return None if pack is None else frozenset(m.id for m in pack.meanings)


def default_location() -> Path:
    """``$EIJA_PACK`` if set, else the pack named by ``packs/default.json``."""
    configured = os.environ.get(ENV_PACK)
    if configured:
        return Path(configured)
    pointer = _read(PACKS_ROOT / DEFAULT_FILE)
    name = pointer.get("pack") if isinstance(pointer, dict) else None
    if not isinstance(name, str) or not name:
        raise PackError([f"{DEFAULT_FILE}: needs a 'pack' name"])
    return PACKS_ROOT / name


@lru_cache(maxsize=8)
def _cached(text: str, name: str) -> Pack:
    return parse_pack(_decode(text, name))


def default_pack() -> Pack:
    """The configured pack, reread on every call and validated from a content-keyed cache."""
    return load_pack(default_location())
