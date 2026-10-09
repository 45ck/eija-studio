# Symbols of domain.pack

# Classes

* [domain.pack.ActionSpec](ActionSpec.md) - The declared guards and required effects of one action; the policy holds every transition to them.
* [domain.pack.Actor](Actor.md) - `class Actor(Contract)` in `domain/pack`.
* [domain.pack.Effect](Effect.md) - A typed effect.
* [domain.pack.Effects](Effects.md) - `class Effects(Contract)` in `domain/pack`.
* [domain.pack.Fixtures](Fixtures.md) - `class Fixtures(Contract)` in `domain/pack`.
* [domain.pack.Journey](Journey.md) - `class Journey(Contract)` in `domain/pack`.
* [domain.pack.Language](Language.md) - `class Language(Contract)` in `domain/pack`.
* [domain.pack.Meaning](Meaning.md) - One interpretation of a request.
* [domain.pack.Pack](Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.PackError](PackError.md) - A pack that cannot be used.
* [domain.pack.PackInfo](PackInfo.md) - `class PackInfo(Contract)` in `domain/pack`.
* [domain.pack.ProposalRule](ProposalRule.md) - Offline fixture: when the lower-cased request contains every ``all`` word and at least one ``any`` word.
* [domain.pack.Proposals](Proposals.md) - `class Proposals(Contract)` in `domain/pack`.
* [domain.pack.Question](Question.md) - A meaning-check question for the owner.
* [domain.pack.Role](Role.md) - A role and the kind of actor that holds it (ADR-0210): a person by default, or an AI agent, a timer or an external system.
* [domain.pack.Term](Term.md) - `class Term(Contract)` in `domain/pack`.
* [domain.pack.Verifier](Verifier.md) - An evidence kind that applies to this pack (``kind`` is the evidence kind's name).

# Constants

* [domain.pack.DEFAULT_FILE](DEFAULT_FILE.md) - Constant `DEFAULT_FILE` in `domain/pack`.
* [domain.pack.ENV_PACK](ENV_PACK.md) - Constant `ENV_PACK` in `domain/pack`.
* [domain.pack.PACKS_ROOT](PACKS_ROOT.md) - Constant `PACKS_ROOT` in `domain/pack`.
* [domain.pack.PACK_FILE](PACK_FILE.md) - Constant `PACK_FILE` in `domain/pack`.
* [domain.pack.PACK_ID](PACK_ID.md) - Constant `PACK_ID` in `domain/pack`.
* [domain.pack.PACK_SCHEMA](PACK_SCHEMA.md) - Constant `PACK_SCHEMA` in `domain/pack`.
* [domain.pack.REPO_URI](REPO_URI.md) - Constant `REPO_URI` in `domain/pack`.

# Functions

* [domain.pack.coherence_problems](coherence_problems.md) - Every cross-reference defect of a structurally valid pack, sorted.
* [domain.pack.default_location](default_location.md) - ``$EIJA_PACK`` if set, else the pack named by ``packs/default.json``.
* [domain.pack.default_pack](default_pack.md) - The configured pack, reread on every call and validated from a content-keyed cache.
* [domain.pack.derive](derive.md) - A draft of `pack` held in memory (`document`, checked as `parse_pack` checks any pack), whose files beside `pack.json` (`data.json`, `screens.json`, `scenarios.json`) are read from where `pack` was read, or are the ones…
* [domain.pack.find_pack](find_pack.md) - Resolve a loaded snapshot by digest, or an unambiguous id after refreshing its sources.
* [domain.pack.held](held.md) - What a draft holds as its file `name` (see `hold`), or None to read the file from the pack's folder.
* [domain.pack.hold](hold.md) - A draft of `pack` that holds `content` in memory as its file `name` beside `pack.json` (such as a draft data model for `data.json`, ADR-0202).
* [domain.pack.load_pack](load_pack.md) - Read current file contents and retain an immutable, digest-addressed pack snapshot.
* [domain.pack.meaning_ids](meaning_ids.md) - The meaning ids of the pack a workflow belongs to, or None when no such pack can be found.
* [domain.pack.pack_directory](pack_directory.md) - The directory this exact pack snapshot was read from, or its authored directory, so optional files beside `pack.json` (such as `data.json`) are read from the same place as the pack.
* [domain.pack.parse_pack](parse_pack.md) - Validate a decoded JSON document as a pack.
* [domain.pack.state_sets](state_sets.md) - The state sets a workflow of this pack can have: the baseline's, and the baseline's after each supported meaning (states its transactions add or remove).
* [domain.pack.ui_key](ui_key.md) - The derived UI/UML key of a pack element: ``data-eija-id="<pack>.<kind>.<id>"``.

# Methods

* [domain.pack.Pack.action](Pack.action.md) - `def action(self, name: str) -> ActionSpec | None` in `domain/pack`.
* [domain.pack.Pack.digest](Pack.digest.md) - `def digest(self) -> str` in `domain/pack`.
* [domain.pack.Pack.effect](Pack.effect.md) - `def effect(self, effect_id: str) -> Effect | None` in `domain/pack`.
* [domain.pack.Pack.id](Pack.id.md) - `def id(self) -> str` in `domain/pack`.
* [domain.pack.Pack.meaning](Pack.meaning.md) - `def meaning(self, meaning_id: str) -> Meaning | None` in `domain/pack`.
* [domain.pack.Pack.role_kind](Pack.role_kind.md) - The kind of actor holding `role`, or None for a role this pack does not declare.
* [domain.pack.Pack.verifier](Pack.verifier.md) - `def verifier(self, kind: str) -> Verifier | None` in `domain/pack`.
