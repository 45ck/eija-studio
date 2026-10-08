---
type: Class
title: domain.models.Workflow
description: Immutable typed states, transitions, roles, guards and effect declarations with a normalised semantic hash.
resource: repo://src/eija_studio/domain/models.py#Workflow
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#Workflow
  title: domain/models.py
  hash_method: ast-sig-v1
  sha256: cd4c79ed175d0127c702005e2d3c5217d60375e845fb74416f86e20d6aed1afe
description_override: Immutable typed states, transitions, roles, guards and effect declarations with a normalised semantic hash.
notes_baseline: 146394bf54a98c962cfd548bd4eaef511de8b00520b35d2fc43f3e92c08af796
verified:
- by: process:eija-wbs-1.3-agent
  at: '2026-09-29T08:20:47Z'
  notes_sha256: a7a288f44c012d29c8086d7d6d28fe61a78c750f991c1d8043493b5a12c2606e
  sources_sha256: 146394bf54a98c962cfd548bd4eaef511de8b00520b35d2fc43f3e92c08af796
---

# domain.models.Workflow

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `class Workflow(Contract)` |
| Code | `repo://src/eija_studio/domain/models.py#Workflow` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `schema_version` | `Literal['eija.workflow.v1']` | `'eija.workflow.v1'` |
| `id` | `str` | `Field(pattern='^[a-z][a-z0-9-]{0,39}$')` |
| `initial_state` | `str` |  |
| `states` | `tuple[str, ...]` | `Field(min_length=1, max_length=32)` |
| `transitions` | `tuple[Transition, ...]` | `Field(min_length=1, max_length=64)` |

## Methods

* [`coherent`](/symbols/domain/models/Workflow.coherent.md) - `def coherent(self) -> Workflow`
* [`semantic_hash`](/symbols/domain/models/Workflow.semantic_hash.md) - `def semantic_hash(self) -> str`
<!-- okf:generated:end facts -->

## Notes

The executable model behind [Workflow Definition](/language/workflow-definition.md). The validator [coherent](/symbols/domain/models/Workflow.coherent.md) rejects dangling states and duplicate or ambiguous transitions; [semantic_hash](/symbols/domain/models/Workflow.semantic_hash.md) is the identity that evidence and preview instances bind to.

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models`.

## Referenced by

* [Execution](/contexts/execution.md) - Owns Trusted fixture actor state, preview instances, command replay, committed effect intents
* [Workflow Definition](/language/workflow-definition.md) - Immutable typed states/transitions/roles/guards/effect declarations.
* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
* [application.appgen.oracle_cases](/symbols/application/appgen/oracle_cases.md) - Every state x action x actor x expected version, then the same request replayed.
* [application.appgen.readme](/symbols/application/appgen/readme.md) - `def readme(pack: Pack, model: Workflow, cases: int) -> str` in `application/appgen`.
* [application.compiler.subject_for](/symbols/application/compiler/subject_for.md) - `def subject_for(model: Workflow, layout: dict[str, Any], identity: dict[str, Any]) -> dict[str, Any]` in `application/compiler`.
* [application.diagram_catalog.case_diagrams](/symbols/application/diagram_catalog/case_diagrams.md) - Every view for one change case as one JSON-friendly payload.
* [application.diagram_catalog.demo_pair](/symbols/application/diagram_catalog/demo_pair.md) - Baseline and the demo candidate: the default pack's baseline with its first supported meaning applied.
* [application.diagram_catalog.html_panels](/symbols/application/diagram_catalog/html_panels.md) - (heading, note, Mermaid text) for `eija render --format html`.
* [application.diagram_catalog.render_view](/symbols/application/diagram_catalog/render_view.md) - Generated diagram text for one view.
* [application.diagrams.CONTRACTS](/symbols/application/diagrams/CONTRACTS.md) - Constant `CONTRACTS` in `application/diagrams`.
* [application.diagrams.commit_sequence](/symbols/application/diagrams/commit_sequence.md) - The commit protocol of one action, in the order `application.runtime.execute` runs it: authority is checked BEFORE any replay lookup, then replay/operation bin…
* [application.diagrams.diff_graph](/symbols/application/diagrams/diff_graph.md) - Baseline vs candidate on one canvas.
* [application.diagrams.diff_summary](/symbols/application/diagrams/diff_summary.md) - Structured diff of two workflows: states, and transitions by action with each changed field's before and after.
* [application.diagrams.impact_graph](/symbols/application/diagrams/impact_graph.md) - The ripple of a change through the modelled dependency chain, taken from `domain.impact.model_impact`: changed rules -> runtime -> state view -> journey -> obl…
* [application.diagrams.journey_graph](/symbols/application/diagrams/journey_graph.md) - One swim-lane per role listing exactly the transitions that role may perform.
* [application.diagrams.policy_violations](/symbols/application/diagrams/policy_violations.md) - Codes `domain.policy.check_policy` reports for `workflow` (empty: the protected policy accepts it).
* [application.diagrams.state_graph](/symbols/application/diagrams/state_graph.md) - The state machine exactly as the runtime interprets it: states, and one edge per transition.
* [application.edit_preview.EditPreview](/symbols/application/edit_preview/EditPreview.md) - An uncommitted candidate bound to a captured case revision; no evidence or edit authority.
* [application.formal.attach](/symbols/application/formal/attach.md) - Sealed receipts for every registered kind the source returned, skipping an exact repeat of the latest one.
* [application.formal.what_if_model](/symbols/application/formal/what_if_model.md) - The workflow an unsupported interpretation would produce, or None (supported, unknown, or no transactions).
* [application.history.SemanticHistory](/symbols/application/history/SemanticHistory.md) - Validated replay; models includes the selected meaning followed by each applied owner edit.
* [application.history.command_event](/symbols/application/history/command_event.md) - Append-only command provenance; decision and receipt payloads remain in their existing audit.
* [application.ports.EditProposer](/symbols/application/ports/EditProposer.md) - Offline request resolution only; returns an untrusted transaction and performs no IO or persistence.
* [application.ports.FormalEvidenceSource](/symbols/application/ports/FormalEvidenceSource.md) - Where formal artifacts come from (Docker, Java, z3 or saved reports are adapter prerequisites).
* [application.ports.ProposalProvider](/symbols/application/ports/ProposalProvider.md) - `class ProposalProvider(Protocol)` in `application/ports`.
* [application.ports.UnitOfWork](/symbols/application/ports/UnitOfWork.md) - All mutations on this port commit together or roll back together.
* [application.runtime.execute](/symbols/application/runtime/execute.md) - `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault: Callable[[…` in `application/runtime`.
* [application.runtime.initialise](/symbols/application/runtime/initialise.md) - `def initialise(session: UnitOfWork, case_id: str, model: Workflow, *, state: str | None=None, pack: Pack | No…` in `application/runtime`.
* [application.service.Studio.create](/symbols/application/service/Studio.create.md) - `def create(self, request: str) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.formal_view](/symbols/application/service/Studio.formal_view.md) - Formal evidence for a bare workflow (``eija compile``): collected and sealed in memory, never stored, never a decision.
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio` in `application/service`.
* [application.service.Studio.workflows](/symbols/application/service/Studio.workflows.md) - Baseline and candidate of a case, for read-only projections (diagrams).
* [application.verifier.verify_runtime](/symbols/application/verifier/verify_runtime.md) - `def verify_runtime(model: Workflow, subject: dict[str, Any], sandbox: SandboxFactory, pack: Pack | None=None)…` in `application/verifier`.
* [application.witness_inspection.InspectionModel](/symbols/application/witness_inspection/InspectionModel.md) - A supplied specimen, a validated projection of it, or an explicit absence of model data.
* [domain.affordance.affordances](/symbols/domain/affordance/affordances.md) - Every single-step retarget and role change of ``model``, each with its dry-run verdict.
* [domain.affordance.dry_run](/symbols/domain/affordance/dry_run.md) - {legal, codes, refs} of applying ``tx`` to ``model`` under ``pack``, without applying it anywhere.
* [domain.change_case.ChangeCase.executable](/symbols/domain/change_case/ChangeCase.executable.md) - `def executable(self) -> Workflow` in `domain/change_case`.
* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.
* [domain.evidence.expected_shape](/symbols/domain/evidence/expected_shape.md) - The runtime matrix a receipt must cover under ``pack``: exactly ``model``'s states when it is known.
* [domain.impact.model_impact](/symbols/domain/impact/model_impact.md) - `def model_impact(before: Workflow, after: Workflow) -> dict[str, Any]` in `domain/impact`.
* [domain.laws.evaluate_table](/symbols/domain/laws/evaluate_table.md) - Every violation of the applicable laws by the workflow's transition table, in law order.
* [domain.models.Workflow.coherent](/symbols/domain/models/Workflow.coherent.md) - `def coherent(self) -> Workflow` in `domain/models`.
* [domain.models.Workflow.semantic_hash](/symbols/domain/models/Workflow.semantic_hash.md) - `def semantic_hash(self) -> str` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.policy.apply_meaning](/symbols/domain/policy/apply_meaning.md) - The candidate a supported pack meaning produces from ``model`` (policy-checked).
* [domain.policy.apply_structural_all](/symbols/domain/policy/apply_structural_all.md) - ``model`` with every transaction applied in order; structure only, no policy (what-if and meaning previews).
* [domain.policy.apply_transaction](/symbols/domain/policy/apply_transaction.md) - Apply one transaction (policy-checked).
* [domain.policy.apply_transactions](/symbols/domain/policy/apply_transactions.md) - Apply an edit sequence as one change: the start must conform, the result must conform (intermediate steps need only be coherent workflows).
* [domain.policy.baseline](/symbols/domain/policy/baseline.md) - The pack's baseline workflow.
* [domain.policy.check_policy](/symbols/domain/policy/check_policy.md) - Sorted, de-duplicated policy codes of ``model`` under the pack (empty means the model conforms).
* [domain.policy.declared_codes](/symbols/domain/policy/declared_codes.md) - Every transition must perform a declared action, with exactly its declared guards and required effects, and must declare every pack-forbidden effect forbidden.
* [domain.policy.demo_candidate](/symbols/domain/policy/demo_candidate.md) - The pack's baseline with its first supported meaning applied.
* [domain.policy.ensure_policy](/symbols/domain/policy/ensure_policy.md) - `def ensure_policy(model: Workflow, pack: Pack | None=None) -> None` in `domain/policy`.
* [domain.policy.law_violations](/symbols/domain/policy/law_violations.md) - `def law_violations(model: Workflow, pack: Pack | None=None) -> list[Violation]` in `domain/policy`.
* [domain.policy.meaning_questions](/symbols/domain/policy/meaning_questions.md) - The pack's meaning-check questions, with expected answers read from the model where the pack says so.
* [domain.policy.policy_refs](/symbols/domain/policy/policy_refs.md) - The laws and model elements a refusal points at (``law:<id>``, ``transition:<id>``, ``state:<id>``), sorted.
* [domain.policy.projections](/symbols/domain/policy/projections.md) - Journey wording and rules derive from executable transitions, not AI copy.
* [domain.policy.what_if](/symbols/domain/policy/what_if.md) - What an UNSUPPORTED meaning would do to ``model`` (structure only, never a candidate), or None when it declares no transactions or they do not even apply struc…
* [domain.transactions.apply_structural](/symbols/domain/transactions/apply_structural.md) - ``model`` with ``tx`` applied.
<!-- okf:generated:end links -->
