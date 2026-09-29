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
* [domain.pack.Role](Role.md) - `class Role(Contract)` in `domain/pack`.
* [domain.pack.Term](Term.md) - `class Term(Contract)` in `domain/pack`.
* [domain.pack.Verifier](Verifier.md) - An evidence kind that applies to this pack.

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
* [domain.pack.default_pack](default_pack.md) - The configured pack (cached per location).
* [domain.pack.load_pack](load_pack.md) - Load a pack from a directory holding ``pack.json`` or from the file itself.
* [domain.pack.meaning_ids](meaning_ids.md) - The meaning ids of the pack a workflow belongs to (``Workflow.id``): a pack loaded in this process, else the repository pack of that id.
* [domain.pack.parse_pack](parse_pack.md) - Validate a decoded JSON document as a pack.
* [domain.pack.state_sets](state_sets.md) - The state sets a workflow of this pack can have: the baseline's, and the baseline's after each supported meaning (states its transactions add or remove).
* [domain.pack.ui_key](ui_key.md) - The derived UI/UML key of a pack element: ``data-eija-id="<pack>.<kind>.<id>"``.

# Methods

* [domain.pack.Pack.action](Pack.action.md) - `def action(self, name: str) -> ActionSpec | None` in `domain/pack`.
* [domain.pack.Pack.digest](Pack.digest.md) - `def digest(self) -> str` in `domain/pack`.
* [domain.pack.Pack.effect](Pack.effect.md) - `def effect(self, effect_id: str) -> Effect | None` in `domain/pack`.
* [domain.pack.Pack.id](Pack.id.md) - `def id(self) -> str` in `domain/pack`.
* [domain.pack.Pack.meaning](Pack.meaning.md) - `def meaning(self, meaning_id: str) -> Meaning | None` in `domain/pack`.
