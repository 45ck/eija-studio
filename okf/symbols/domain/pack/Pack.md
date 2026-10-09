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
  sha256: bccf0814306f4e9611d5f87c73a8fdfc49fd4703d191813b7ba27c447b82a811
notes_baseline: 4a3a5a0bf346c0e0ae6024a773f947b746083dd34ce9430baf208e67f3792ea4
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
| `_held` | `dict[str, Any]` | `PrivateAttr(default_factory=dict)` |

## Methods

* [`action`](/symbols/domain/pack/Pack.action.md) - `def action(self, name: str) -> ActionSpec \| None`
* [`digest`](/symbols/domain/pack/Pack.digest.md) - `def digest(self) -> str`
* [`effect`](/symbols/domain/pack/Pack.effect.md) - `def effect(self, effect_id: str) -> Effect \| None`
* [`id`](/symbols/domain/pack/Pack.id.md) - `def id(self) -> str`
* [`meaning`](/symbols/domain/pack/Pack.meaning.md) - `def meaning(self, meaning_id: str) -> Meaning \| None`
* [`role_kind`](/symbols/domain/pack/Pack.role_kind.md) - `def role_kind(self, role: str) -> str \| None`
* [`verifier`](/symbols/domain/pack/Pack.verifier.md) - `def verifier(self, kind: str) -> Verifier \| None`
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
* [domain.pack.Role](/symbols/domain/pack/Role.md) - A role and the kind of actor that holds it (ADR-0210): a person by default, or an AI agent, a timer or an external system.
* [domain.pack.Verifier](/symbols/domain/pack/Verifier.md) - An evidence kind that applies to this pack (``kind`` is the evidence kind's name).

## Referenced by

* [application.access.access](/symbols/application/access/access.md) - The matrix for `model`, and, when `base` differs, the permissions it adds and removes compared with `base`.
* [application.access.matrix](/symbols/application/access/matrix.md) - Every role's actions from every state, each tried in the kernel with the fixture actors in that role.
* [application.access.reach](/symbols/application/access/reach.md) - Can a record reach `target` with no step taken by role `without` (or at all, when it is None)?
* [application.appgen.data_cases](/symbols/application/appgen/data_cases.md) - Record values to create with, and `check_values`' answer for each: a valid record, then each required value missing, each value of the wrong type, each text on…
* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
* [application.appgen.oracle_cases](/symbols/application/appgen/oracle_cases.md) - Every state x action x actor x expected version, then the same request replayed.
* [application.appgen.readme](/symbols/application/appgen/readme.md) - `def readme(pack: Pack, model: Workflow, cases: int, data: DataModel | None=None) -> str` in `application/appgen`.
* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],…` in `application/compiler`.
* [application.data_steps.draft_pack](/symbols/application/data_steps/draft_pack.md) - `pack` as these plan steps would have it, held in memory: on a system the person started (`grows`), the actions and roles they name are declared (ADR-0201) and…
* [application.edit_preview.preview_edit](/symbols/application/edit_preview/preview_edit.md) - The candidate edit would produce from this snapshot, or its refusal without a guessed model.
* [application.edit_proposal.propose_edit](/symbols/application/edit_proposal/propose_edit.md) - No persistence or evidence: resolve one request, then use the existing policy-checked projection.
* [application.formal.attach](/symbols/application/formal/attach.md) - Sealed receipts for every registered kind the source returned, skipping an exact repeat of the latest one.
* [application.formal.for_pack](/symbols/application/formal/for_pack.md) - Artifacts of a kind this pack does not verify from the reports become one NOT_RUN artifact with the pack's reason.
* [application.formal.pack_not_run](/symbols/application/formal/pack_not_run.md) - Why ``kind`` is NOT_RUN for ``pack`` (None when the pack verifies it from the checkout's reports).
* [application.formal.packet_view](/symbols/application/formal/packet_view.md) - The formal part of the review packet: per-kind claims, blockers, the full evidence list, explanations, and (with a pack) the pack's declared verifiers, so a ki…
* [application.formal.verifier_view](/symbols/application/formal/verifier_view.md) - Every verifier the pack declares, with the status its mode implies before any evidence is read: a kind that is not produced for this pack (``not_run``) is NOT_…
* [application.formal.what_if_model](/symbols/application/formal/what_if_model.md) - The workflow an unsupported interpretation would produce, or None (supported, unknown, or no transactions).
* [application.history.history_view](/symbols/application/history/history_view.md) - Read-only models for navigation plus actual command audit entries; no invented legacy timestamps.
* [application.history.replay](/symbols/application/history/replay.md) - Fail closed when stored commands no longer explain the candidate under the exact active pack.
* [application.law_proof.actor_classes](/symbols/application/law_proof/actor_classes.md) - One actor per role (declared or used) and per combination of `active` and `assigned`, and an outsider.
* [application.law_proof.compare_laws](/symbols/application/law_proof/compare_laws.md) - Which laws a draft adds, removes or changes.
* [application.law_proof.prove_laws](/symbols/application/law_proof/prove_laws.md) - Every law of the pack, judged on `model` (the pack's own by default), with the evidence for each verdict.
* [application.law_proof.with_laws](/symbols/application/law_proof/with_laws.md) - The pack with its law file replaced by `laws` (a draft edited in PlayIDE), checked as the pack loader checks it.
* [application.memo.ensure_conforms](/symbols/application/memo/ensure_conforms.md) - `ensure(model, pack)` (the policy check): a pair it let through is remembered; any other is refused by it again, so the error is always the check's own.
* [application.new_system.classes](/symbols/application/new_system/classes.md) - A system's record class and each class's attribute names, for naming data-model steps (ADR-0202); None when the system has no class diagram.
* [application.new_system.declare](/symbols/application/new_system/declare.md) - `pack` with every action and role `transactions` name but it does not declare yet, declared exactly as a sketch declares them (ADR-0201): an action gets the ba…
* [application.new_system.new_names](/symbols/application/new_system/new_names.md) - The actions and roles `transactions` name that `pack` does not declare, in order of first use.
* [application.new_system.template_documents](/symbols/application/new_system/template_documents.md) - A copy of a template's documents as a new system: new id and name, the same model, rules, laws, screens and test cases (`scenarios.json`).
* [application.plan.describe](/symbols/application/plan/describe.md) - One line a person can check against the diagram.
* [application.plan.example_passes](/symbols/application/plan/example_passes.md) - Whether `request`, sent to the chat as it stands, becomes a plan the policy allows on `model`.
* [application.plan.preview_plan](/symbols/application/plan/preview_plan.md) - What the accepted steps would make of `model`.
* [application.plan.propose_plan](/symbols/application/plan/propose_plan.md) - Ask the proposer for a plan, re-check it, and preview it with every step accepted.
* [application.ports.PlanProposer](/symbols/application/ports/PlanProposer.md) - Turns a chat request into {summary, meaning, steps: [{transaction, why}]}.
* [application.review.behaviour_diff](/symbols/application/review/behaviour_diff.md) - Every fixture actor tries every action from every state on both models; the attempts whose outcome differs.
* [application.review.review_change](/symbols/application/review/review_change.md) - Everything a reviewer needs to check a change: what changed, how risky, and what the kernel does differently.
* [application.ripple.check_follow_ons](/symbols/application/ripple/check_follow_ons.md) - The proposer's follow-on steps, each re-checked on its own on top of the plan: a state-machine step through the policy (`base` with `plan` and the step), a scr…
* [application.runtime.execute](/symbols/application/runtime/execute.md) - `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault: Callable[[…` in `application/runtime`.
* [application.runtime.initialise](/symbols/application/runtime/initialise.md) - `def initialise(session: UnitOfWork, case_id: str, model: Workflow, *, state: str | None=None, pack: Pack | No…` in `application/runtime`.
* [application.scenario_run.record_steps](/symbols/application/scenario_run/record_steps.md) - What the kernel does for each (actor, action) in turn, written as scenario steps that expect exactly that.
* [application.scenario_run.run_scenario](/symbols/application/scenario_run/run_scenario.md) - Run one scenario; it stops at the first step whose outcome differs from what it expects.
* [application.scenario_run.run_scenarios](/symbols/application/scenario_run/run_scenarios.md) - Every scenario run on `model`; a model the policy refuses runs none of them.
* [application.scxml.to_scxml](/symbols/application/scxml/to_scxml.md) - The model as an SCXML document.
* [application.sequence_layout.place](/symbols/application/sequence_layout/place.md) - `def place(pack: Pack, scenario: Scenario, start: str, steps: list[dict[str, Any]], record: tuple[str, str]) -…` in `application/sequence_layout`.
* [application.sequences.check_sequences](/symbols/application/sequences/check_sequences.md) - Every scenario drawn as a sequence and checked by the kernel on `model`; with `base` (the model in force) also on it, for the change.
* [application.sequences.record_name](/symbols/application/sequences/record_name.md) - The record lifeline's name and its class: `loan : Loan` when the pack has a data model.
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio` in `application/service`.
* [application.simulation.MemorySession](/symbols/application/simulation/MemorySession.md) - The kernel's unit-of-work port over plain dictionaries, keeping every record, operation and effect.
* [application.simulation.run_log](/symbols/application/simulation/run_log.md) - Every step of the seeded run in order, and where a run with these breakpoints stops (ADR-0160).
* [application.simulation.simulate](/symbols/application/simulation/simulate.md) - Run `steps` seeded attempts by the pack's fixture actors through the kernel and report where they went.
* [application.verifier.verify_runtime](/symbols/application/verifier/verify_runtime.md) - `def verify_runtime(model: Workflow, subject: dict[str, Any], sandbox: SandboxFactory, pack: Pack | None=None)…` in `application/verifier`.
* [application.witness_inspection.inspect_verdict](/symbols/application/witness_inspection/inspect_verdict.md) - Project only the deciding receipt, retaining uncertainty and all recorded raw data without writes.
* [domain.affordance.affordances](/symbols/domain/affordance/affordances.md) - Every single-step retarget and role change of ``model``, each with its dry-run verdict.
* [domain.affordance.dry_run](/symbols/domain/affordance/dry_run.md) - {legal, codes, refs} of applying ``tx`` to ``model`` under ``pack``, without applying it anywhere.
* [domain.data.data_for](/symbols/domain/data/data_for.md) - The data model beside this pack's `pack.json`, if it has one: the one a draft holds (ADR-0202), else `data.json`.
* [domain.evidence.expected_shape](/symbols/domain/evidence/expected_shape.md) - The runtime matrix a receipt must cover under ``pack``: exactly ``model``'s states when it is known.
* [domain.pack.Pack.action](/symbols/domain/pack/Pack.action.md) - `def action(self, name: str) -> ActionSpec | None` in `domain/pack`.
* [domain.pack.Pack.digest](/symbols/domain/pack/Pack.digest.md) - `def digest(self) -> str` in `domain/pack`.
* [domain.pack.Pack.effect](/symbols/domain/pack/Pack.effect.md) - `def effect(self, effect_id: str) -> Effect | None` in `domain/pack`.
* [domain.pack.Pack.id](/symbols/domain/pack/Pack.id.md) - `def id(self) -> str` in `domain/pack`.
* [domain.pack.Pack.meaning](/symbols/domain/pack/Pack.meaning.md) - `def meaning(self, meaning_id: str) -> Meaning | None` in `domain/pack`.
* [domain.pack.Pack.role_kind](/symbols/domain/pack/Pack.role_kind.md) - The kind of actor holding `role`, or None for a role this pack does not declare.
* [domain.pack.Pack.verifier](/symbols/domain/pack/Pack.verifier.md) - `def verifier(self, kind: str) -> Verifier | None` in `domain/pack`.
* [domain.pack.coherence_problems](/symbols/domain/pack/coherence_problems.md) - Every cross-reference defect of a structurally valid pack, sorted.
* [domain.pack.default_pack](/symbols/domain/pack/default_pack.md) - The configured pack, reread on every call and validated from a content-keyed cache.
* [domain.pack.derive](/symbols/domain/pack/derive.md) - A draft of `pack` held in memory (`document`, checked as `parse_pack` checks any pack), whose files beside `pack.json` (`data.json`, `screens.json`, `scenarios…
* [domain.pack.find_pack](/symbols/domain/pack/find_pack.md) - Resolve a loaded snapshot by digest, or an unambiguous id after refreshing its sources.
* [domain.pack.held](/symbols/domain/pack/held.md) - What a draft holds as its file `name` (see `hold`), or None to read the file from the pack's folder.
* [domain.pack.hold](/symbols/domain/pack/hold.md) - A draft of `pack` that holds `content` in memory as its file `name` beside `pack.json` (such as a draft data model for `data.json`, ADR-0202).
* [domain.pack.load_pack](/symbols/domain/pack/load_pack.md) - Read current file contents and retain an immutable, digest-addressed pack snapshot.
* [domain.pack.pack_directory](/symbols/domain/pack/pack_directory.md) - The directory this exact pack snapshot was read from, or its authored directory, so optional files beside `pack.json` (such as `data.json`) are read from the s…
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
* [domain.scenarios.scenarios_for](/symbols/domain/scenarios/scenarios_for.md) - The scenarios beside this pack's `pack.json`, or none.
* [domain.screens.default_screens](/symbols/domain/screens/default_screens.md) - One default screen per use case.
* [domain.screens.screens_for](/symbols/domain/screens/screens_for.md) - The screens beside this pack's `pack.json`, each use case they leave out given its default screen; or the defaults.
<!-- okf:generated:end links -->
