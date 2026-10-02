---
type: Module
title: domain.pack
description: 'Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).'
resource: repo://src/eija_studio/domain/pack.py
tags:
- module
- domain
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py
  title: domain/pack.py
  hash_method: ast-api-v1
  sha256: d183d00906ed7e078ca45886325e319d97ecdd69c26476cfa993a418909e3639
notes_baseline: 2a5027578fe2cfd7c1908194ea28def39bd21e2a0408cd747613c5eb7eb1bb04
---

# domain.pack

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | domain |
| Code | `repo://src/eija_studio/domain/pack.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

A pack is data, never code: the baseline workflow (``model``), its roles, the declared action catalog
(guards and required effects per action), typed effects, laws, the meanings an owner may select, the
language terms with ``repo://`` bindings, offline fixtures (actors, proposals, demo request), the verifiers
that apply, and the review journey. Generic code reads a pack; it never names a pack's states, roles or actions.

Loading is total: any defect (unreadable file, bad JSON, wrong shape, a reference to an undeclared state, role,
action or effect) becomes ``PackError`` (code ``PACK_INVALID``) with SORTED diagnostics. It never crashes.
~~~

## Public symbols

* [`ActionSpec`](/symbols/domain/pack/ActionSpec.md) (class) - The declared guards and required effects of one action; the policy holds every transition to them.
* [`Actor`](/symbols/domain/pack/Actor.md) (class) - no docstring
* [`DEFAULT_FILE`](/symbols/domain/pack/DEFAULT_FILE.md) (constant) - no docstring
* [`ENV_PACK`](/symbols/domain/pack/ENV_PACK.md) (constant) - no docstring
* [`Effect`](/symbols/domain/pack/Effect.md) (class) - A typed effect.
* [`Effects`](/symbols/domain/pack/Effects.md) (class) - no docstring
* [`Fixtures`](/symbols/domain/pack/Fixtures.md) (class) - no docstring
* [`Journey`](/symbols/domain/pack/Journey.md) (class) - no docstring
* [`Language`](/symbols/domain/pack/Language.md) (class) - no docstring
* [`Meaning`](/symbols/domain/pack/Meaning.md) (class) - One interpretation of a request.
* [`PACKS_ROOT`](/symbols/domain/pack/PACKS_ROOT.md) (constant) - no docstring
* [`PACK_FILE`](/symbols/domain/pack/PACK_FILE.md) (constant) - no docstring
* [`PACK_ID`](/symbols/domain/pack/PACK_ID.md) (constant) - no docstring
* [`PACK_SCHEMA`](/symbols/domain/pack/PACK_SCHEMA.md) (constant) - no docstring
* [`Pack`](/symbols/domain/pack/Pack.md) (class) - no docstring
* [`PackError`](/symbols/domain/pack/PackError.md) (class) - A pack that cannot be used.
* [`PackInfo`](/symbols/domain/pack/PackInfo.md) (class) - no docstring
* [`ProposalRule`](/symbols/domain/pack/ProposalRule.md) (class) - Offline fixture: when the lower-cased request contains every ``all`` word and at least one ``any`` word.
* [`Proposals`](/symbols/domain/pack/Proposals.md) (class) - no docstring
* [`Question`](/symbols/domain/pack/Question.md) (class) - A meaning-check question for the owner.
* [`REPO_URI`](/symbols/domain/pack/REPO_URI.md) (constant) - no docstring
* [`Role`](/symbols/domain/pack/Role.md) (class) - no docstring
* [`Term`](/symbols/domain/pack/Term.md) (class) - no docstring
* [`Verifier`](/symbols/domain/pack/Verifier.md) (class) - An evidence kind that applies to this pack (``kind`` is the evidence kind's name).
* [`coherence_problems`](/symbols/domain/pack/coherence_problems.md) (function) - Every cross-reference defect of a structurally valid pack, sorted.
* [`default_location`](/symbols/domain/pack/default_location.md) (function) - ``$EIJA_PACK`` if set, else the pack named by ``packs/default.json``.
* [`default_pack`](/symbols/domain/pack/default_pack.md) (function) - The configured pack, reread on every call and validated from a content-keyed cache.
* [`find_pack`](/symbols/domain/pack/find_pack.md) (function) - Resolve a loaded snapshot by digest, or an unambiguous id after refreshing its sources.
* [`load_pack`](/symbols/domain/pack/load_pack.md) (function) - Read current file contents and retain an immutable, digest-addressed pack snapshot.
* [`meaning_ids`](/symbols/domain/pack/meaning_ids.md) (function) - The meaning ids of the pack a workflow belongs to, or None when no such pack can be found.
* [`parse_pack`](/symbols/domain/pack/parse_pack.md) (function) - Validate a decoded JSON document as a pack.
* [`state_sets`](/symbols/domain/pack/state_sets.md) (function) - The state sets a workflow of this pack can have: the baseline's, and the baseline's after each supported meaning (state…
* [`ui_key`](/symbols/domain/pack/ui_key.md) (function) - The derived UI/UML key of a pack element: ``data-eija-id="<pack>.<kind>.<id>"``.

## Internal imports

* [`domain/laws`](/modules/domain/laws.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/transactions`](/modules/domain/transactions.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.laws](/modules/domain/laws.md) - Typed law DSL of a domain pack: what a workflow may never do, stated as data (WBS 1.1/1.2).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.transactions](/modules/domain/transactions.md) - Open change vocabulary (WBS 1.3): the semantic edits an owner (or a pack meaning) may make to a workflow.

## Referenced by

* [adapters.identity](/modules/adapters/identity.md) - Measured release identity, not a proof of correctness or author authenticity.
* [adapters.repository](/modules/adapters/repository.md) - Repository analysis and bounded source navigation over captured checkout bytes.
* [adapters.repository_analysis](/modules/adapters/repository_analysis.md) - Captured-byte syntax and partial impact adapted to existing Weave primitives.
* [adapters.repository_change_snapshot](/modules/adapters/repository_change_snapshot.md) - Captured immutable comparison snapshots shared by capture, analysis and retention.
* [adapters.repository_changes](/modules/adapters/repository_changes.md) - Read-only, bounded comparison of two local Git commits.
* [adapters.self_facts](/modules/adapters/self_facts.md) - Syntactic facts about EIJA's own review implementation, never a conformance proof.
* [adapters.sqlite_store](/modules/adapters/sqlite_store.md) - Durable local unit of work.
* [application.compiler](/modules/application/compiler.md) - Compiler: model → projections + impacts + obligations + computed review packet.
* [application.formal](/modules/application/formal.md) - Formal evidence in the application layer: seal what an adapter collected, and build the packet view.
* [application.history](/modules/application/history.md) - Semantic history is a projection of typed commands, replayed by the existing policy interpreter.
* [application.runtime](/modules/application/runtime.md) - Generic execution algorithm; the domain (policy, laws, typed effects) comes from the pack.
* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
* [application.verifier](/modules/application/verifier.md) - Bounded synthetic runtime experiments.
* [bootstrap](/modules/bootstrap.md) - The only composition root: wires application ports to concrete adapters.
* [domain.affordance](/modules/domain/affordance.md) - Affordance map (WBS 1.3): which single edits the kernel would accept, and why the others are refused.
* [domain.evidence](/modules/domain/evidence.md) - Compatibility is computed.
* [domain.policy](/modules/domain/policy.md) - Generic policy: coherence with a domain pack's declared action catalog, the pack's laws, and declared effects.
* [interfaces.http](/modules/interfaces/http.md) - Loopback-only local adapter.
* [domain.pack.ActionSpec](/symbols/domain/pack/ActionSpec.md) - The declared guards and required effects of one action; the policy holds every transition to them.
* [domain.pack.Actor](/symbols/domain/pack/Actor.md) - `class Actor(Contract)` in `domain/pack`.
* [domain.pack.DEFAULT_FILE](/symbols/domain/pack/DEFAULT_FILE.md) - Constant `DEFAULT_FILE` in `domain/pack`.
* [domain.pack.ENV_PACK](/symbols/domain/pack/ENV_PACK.md) - Constant `ENV_PACK` in `domain/pack`.
* [domain.pack.Effect](/symbols/domain/pack/Effect.md) - A typed effect.
* [domain.pack.Effects](/symbols/domain/pack/Effects.md) - `class Effects(Contract)` in `domain/pack`.
* [domain.pack.Fixtures](/symbols/domain/pack/Fixtures.md) - `class Fixtures(Contract)` in `domain/pack`.
* [domain.pack.Journey](/symbols/domain/pack/Journey.md) - `class Journey(Contract)` in `domain/pack`.
* [domain.pack.Language](/symbols/domain/pack/Language.md) - `class Language(Contract)` in `domain/pack`.
* [domain.pack.Meaning](/symbols/domain/pack/Meaning.md) - One interpretation of a request.
* [domain.pack.PACKS_ROOT](/symbols/domain/pack/PACKS_ROOT.md) - Constant `PACKS_ROOT` in `domain/pack`.
* [domain.pack.PACK_FILE](/symbols/domain/pack/PACK_FILE.md) - Constant `PACK_FILE` in `domain/pack`.
* [domain.pack.PACK_ID](/symbols/domain/pack/PACK_ID.md) - Constant `PACK_ID` in `domain/pack`.
* [domain.pack.PACK_SCHEMA](/symbols/domain/pack/PACK_SCHEMA.md) - Constant `PACK_SCHEMA` in `domain/pack`.
* [domain.pack.Pack.action](/symbols/domain/pack/Pack.action.md) - `def action(self, name: str) -> ActionSpec | None` in `domain/pack`.
* [domain.pack.Pack.digest](/symbols/domain/pack/Pack.digest.md) - `def digest(self) -> str` in `domain/pack`.
* [domain.pack.Pack.effect](/symbols/domain/pack/Pack.effect.md) - `def effect(self, effect_id: str) -> Effect | None` in `domain/pack`.
* [domain.pack.Pack.id](/symbols/domain/pack/Pack.id.md) - `def id(self) -> str` in `domain/pack`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.Pack.meaning](/symbols/domain/pack/Pack.meaning.md) - `def meaning(self, meaning_id: str) -> Meaning | None` in `domain/pack`.
* [domain.pack.Pack.verifier](/symbols/domain/pack/Pack.verifier.md) - `def verifier(self, kind: str) -> Verifier | None` in `domain/pack`.
* [domain.pack.PackError](/symbols/domain/pack/PackError.md) - A pack that cannot be used.
* [domain.pack.PackInfo](/symbols/domain/pack/PackInfo.md) - `class PackInfo(Contract)` in `domain/pack`.
* [domain.pack.ProposalRule](/symbols/domain/pack/ProposalRule.md) - Offline fixture: when the lower-cased request contains every ``all`` word and at least one ``any`` word.
* [domain.pack.Proposals](/symbols/domain/pack/Proposals.md) - `class Proposals(Contract)` in `domain/pack`.
* [domain.pack.Question](/symbols/domain/pack/Question.md) - A meaning-check question for the owner.
* [domain.pack.REPO_URI](/symbols/domain/pack/REPO_URI.md) - Constant `REPO_URI` in `domain/pack`.
* [domain.pack.Role](/symbols/domain/pack/Role.md) - `class Role(Contract)` in `domain/pack`.
* [domain.pack.Term](/symbols/domain/pack/Term.md) - `class Term(Contract)` in `domain/pack`.
* [domain.pack.Verifier](/symbols/domain/pack/Verifier.md) - An evidence kind that applies to this pack (``kind`` is the evidence kind's name).
* [domain.pack.coherence_problems](/symbols/domain/pack/coherence_problems.md) - Every cross-reference defect of a structurally valid pack, sorted.
* [domain.pack.default_location](/symbols/domain/pack/default_location.md) - ``$EIJA_PACK`` if set, else the pack named by ``packs/default.json``.
* [domain.pack.default_pack](/symbols/domain/pack/default_pack.md) - The configured pack, reread on every call and validated from a content-keyed cache.
* [domain.pack.find_pack](/symbols/domain/pack/find_pack.md) - Resolve a loaded snapshot by digest, or an unambiguous id after refreshing its sources.
* [domain.pack.load_pack](/symbols/domain/pack/load_pack.md) - Read current file contents and retain an immutable, digest-addressed pack snapshot.
* [domain.pack.meaning_ids](/symbols/domain/pack/meaning_ids.md) - The meaning ids of the pack a workflow belongs to, or None when no such pack can be found.
* [domain.pack.parse_pack](/symbols/domain/pack/parse_pack.md) - Validate a decoded JSON document as a pack.
* [domain.pack.state_sets](/symbols/domain/pack/state_sets.md) - The state sets a workflow of this pack can have: the baseline's, and the baseline's after each supported meaning (states its transactions add or remove).
* [domain.pack.ui_key](/symbols/domain/pack/ui_key.md) - The derived UI/UML key of a pack element: ``data-eija-id="<pack>.<kind>.<id>"``.
<!-- okf:generated:end links -->
