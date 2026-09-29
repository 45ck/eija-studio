---
type: Class
title: domain.pack.Pack
description: '`class Pack(Contract)` in `domain/pack`.'
resource: repo://src/eija_studio/domain/pack.py#Pack
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#Pack
  title: domain/pack.py
  hash_method: ast-sig-v1
  sha256: 8d85de04a3a400125e5e52d333e87bd22205afcf296e9b5abbc0db5a7ec3cc98
notes_baseline: 1a514a15a90fe50f64efbd7b406b83d3b229a57dcd56b03f948f256392996630
---

# domain.pack.Pack

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `class Pack(Contract)` |
| Code | `repo://src/eija_studio/domain/pack.py#Pack` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `schema_version` | `Literal['eija.pack.v1']` | `'eija.pack.v1'` |
| `pack` | `PackInfo` |  |
| `model` | `Workflow` |  |
| `roles` | `tuple[Role, ...]` | `Field(min_length=1)` |
| `actions` | `tuple[ActionSpec, ...]` | `Field(min_length=1)` |
| `effects` | `Effects` |  |
| `laws` | `tuple[Law, ...]` | `()` |
| `meanings` | `tuple[Meaning, ...]` | `Field(min_length=1)` |
| `language` | `Language` | `Language()` |
| `fixtures` | `Fixtures` |  |
| `verifiers` | `tuple[Verifier, ...]` | `()` |
| `journey` | `Journey` | `Journey()` |

## Methods

* [`action`](/symbols/domain/pack/Pack.action.md) - `def action(self, name: str) -> ActionSpec \| None`
* [`digest`](/symbols/domain/pack/Pack.digest.md) - `def digest(self) -> str`
* [`effect`](/symbols/domain/pack/Pack.effect.md) - `def effect(self, effect_id: str) -> Effect \| None`
* [`id`](/symbols/domain/pack/Pack.id.md) - `def id(self) -> str`
* [`meaning`](/symbols/domain/pack/Pack.meaning.md) - `def meaning(self, meaning_id: str) -> Meaning \| None`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.laws.Law](/symbols/domain/laws/Law.md) - Type alias `Law` in `domain/laws`.
* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.ActionSpec](/symbols/domain/pack/ActionSpec.md) - The declared guards and required effects of one action; the policy holds every transition to them.
* [domain.pack.Effect](/symbols/domain/pack/Effect.md) - A typed effect.
* [domain.pack.Effects](/symbols/domain/pack/Effects.md) - `class Effects(Contract)` in `domain/pack`.
* [domain.pack.Fixtures](/symbols/domain/pack/Fixtures.md) - `class Fixtures(Contract)` in `domain/pack`.
* [domain.pack.Journey](/symbols/domain/pack/Journey.md) - `class Journey(Contract)` in `domain/pack`.
* [domain.pack.Language](/symbols/domain/pack/Language.md) - `class Language(Contract)` in `domain/pack`.
* [domain.pack.Meaning](/symbols/domain/pack/Meaning.md) - One interpretation of a request.
* [domain.pack.PackInfo](/symbols/domain/pack/PackInfo.md) - `class PackInfo(Contract)` in `domain/pack`.
* [domain.pack.Role](/symbols/domain/pack/Role.md) - `class Role(Contract)` in `domain/pack`.
* [domain.pack.Verifier](/symbols/domain/pack/Verifier.md) - An evidence kind that applies to this pack.

## Referenced by

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],…` in `application/compiler`.
* [application.formal.what_if_model](/symbols/application/formal/what_if_model.md) - The workflow an unsupported interpretation would produce, or None (supported, unknown, or no transactions).
* [application.runtime.execute](/symbols/application/runtime/execute.md) - `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault: Callable[[…` in `application/runtime`.
* [application.runtime.initialise](/symbols/application/runtime/initialise.md) - `def initialise(session: UnitOfWork, case_id: str, model: Workflow, *, state: str | None=None, pack: Pack | No…` in `application/runtime`.
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio` in `application/service`.
* [application.verifier.verify_runtime](/symbols/application/verifier/verify_runtime.md) - `def verify_runtime(model: Workflow, subject: dict[str, Any], sandbox: SandboxFactory, pack: Pack | None=None)…` in `application/verifier`.
* [domain.affordance.affordances](/symbols/domain/affordance/affordances.md) - Every single-step retarget and role change of ``model``, each with its dry-run verdict.
* [domain.affordance.dry_run](/symbols/domain/affordance/dry_run.md) - {legal, codes, refs} of applying ``tx`` to ``model`` under ``pack``, without applying it anywhere.
* [domain.evidence.expected_shape](/symbols/domain/evidence/expected_shape.md) - The runtime matrix a receipt must cover under ``pack``: exactly ``model``'s states when it is known.
* [domain.pack.Pack.action](/symbols/domain/pack/Pack.action.md) - `def action(self, name: str) -> ActionSpec | None` in `domain/pack`.
* [domain.pack.Pack.digest](/symbols/domain/pack/Pack.digest.md) - `def digest(self) -> str` in `domain/pack`.
* [domain.pack.Pack.effect](/symbols/domain/pack/Pack.effect.md) - `def effect(self, effect_id: str) -> Effect | None` in `domain/pack`.
* [domain.pack.Pack.id](/symbols/domain/pack/Pack.id.md) - `def id(self) -> str` in `domain/pack`.
* [domain.pack.Pack.meaning](/symbols/domain/pack/Pack.meaning.md) - `def meaning(self, meaning_id: str) -> Meaning | None` in `domain/pack`.
* [domain.pack.coherence_problems](/symbols/domain/pack/coherence_problems.md) - Every cross-reference defect of a structurally valid pack, sorted.
* [domain.pack.default_pack](/symbols/domain/pack/default_pack.md) - The configured pack (cached per location).
* [domain.pack.load_pack](/symbols/domain/pack/load_pack.md) - Load a pack from a directory holding ``pack.json`` or from the file itself.
* [domain.pack.parse_pack](/symbols/domain/pack/parse_pack.md) - Validate a decoded JSON document as a pack.
* [domain.pack.state_sets](/symbols/domain/pack/state_sets.md) - The state sets a workflow of this pack can have: the baseline's, and the baseline's after each supported meaning (states its transactions add or remove).
* [domain.policy.apply_meaning](/symbols/domain/policy/apply_meaning.md) - The candidate a supported pack meaning produces from ``model`` (policy-checked).
* [domain.policy.apply_structural_all](/symbols/domain/policy/apply_structural_all.md) - ``model`` with every transaction applied in order; structure only, no policy (what-if and meaning previews).
* [domain.policy.apply_transaction](/symbols/domain/policy/apply_transaction.md) - Apply one transaction (policy-checked).
* [domain.policy.apply_transactions](/symbols/domain/policy/apply_transactions.md) - Apply an edit sequence as one change: the start must conform, the result must conform (intermediate steps need only be coherent workflows).
* [domain.policy.baseline](/symbols/domain/policy/baseline.md) - The pack's baseline workflow.
* [domain.policy.check_policy](/symbols/domain/policy/check_policy.md) - Sorted, de-duplicated policy codes of ``model`` under the pack (empty means the model conforms).
* [domain.policy.declared_codes](/symbols/domain/policy/declared_codes.md) - Every transition must perform a declared action, with exactly its declared guards and required effects, and must declare every pack-forbidden effect forbidden.
* [domain.policy.demo_candidate](/symbols/domain/policy/demo_candidate.md) - The pack's baseline with its first supported meaning applied.
* [domain.policy.effects_table](/symbols/domain/policy/effects_table.md) - Declared required effects per action.
* [domain.policy.ensure_policy](/symbols/domain/policy/ensure_policy.md) - `def ensure_policy(model: Workflow, pack: Pack | None=None) -> None` in `domain/policy`.
* [domain.policy.first_supported_meaning](/symbols/domain/policy/first_supported_meaning.md) - The id of the pack's first supported meaning (the demo candidate's meaning).
* [domain.policy.forbidden_effects](/symbols/domain/policy/forbidden_effects.md) - `def forbidden_effects(pack: Pack | None=None) -> tuple[str, ...]` in `domain/policy`.
* [domain.policy.law_violations](/symbols/domain/policy/law_violations.md) - `def law_violations(model: Workflow, pack: Pack | None=None) -> list[Violation]` in `domain/policy`.
* [domain.policy.meaning_options](/symbols/domain/policy/meaning_options.md) - The pack's meanings as the review surface shows them: label, whether supported, consequences.
* [domain.policy.meaning_questions](/symbols/domain/policy/meaning_questions.md) - The pack's meaning-check questions, with expected answers read from the model where the pack says so.
* [domain.policy.meaning_transactions](/symbols/domain/policy/meaning_transactions.md) - `def meaning_transactions(meaning_id: str, pack: Pack | None=None) -> tuple[Transaction, ...]` in `domain/policy`.
* [domain.policy.policy_refs](/symbols/domain/policy/policy_refs.md) - The laws and model elements a refusal points at (``law:<id>``, ``transition:<id>``, ``state:<id>``), sorted.
* [domain.policy.transition](/symbols/domain/policy/transition.md) - A transition for a declared action, with the action's declared guards and effects and the pack's forbidden effects.
* [domain.policy.what_if](/symbols/domain/policy/what_if.md) - What an UNSUPPORTED meaning would do to ``model`` (structure only, never a candidate), or None when it declares no transactions or they do not even apply struc…
<!-- okf:generated:end links -->
