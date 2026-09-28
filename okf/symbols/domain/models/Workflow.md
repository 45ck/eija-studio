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
  sha256: 73b2c816a86d4ea18d6d037d6412348eafd1ffceae0f24357cadc1336c6f48f2
description_override: Immutable typed states, transitions, roles, guards and effect declarations with a normalised semantic hash.
---

# domain.models.Workflow

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `class Workflow(Contract)` |
| Code | `repo://src/eija_studio/domain/models.py#Workflow` |
| Hash | `ast-sig-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `schema_version` | `Literal['eija.workflow.v1']` | `'eija.workflow.v1'` |
| `id` | `Literal['excursion']` | `'excursion'` |
| `initial_state` | `str` | `'Draft'` |
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

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models` (the source has no docstring).
* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models` (the source has no docstring).

## Referenced by

* [Execution](/contexts/execution.md) - Owns Trusted fixture actor state, preview instances, command replay, committed effect intents
* [Workflow Definition](/language/workflow-definition.md) - Immutable typed states/transitions/roles/guards/effect declarations.
* [application.compiler.subject_for](/symbols/application/compiler/subject_for.md) - `def subject_for(model: Workflow, layout: dict, identity: dict) -> dict` in `application/compiler` (the source has no docstring).
* [application.ports.ProposalProvider](/symbols/application/ports/ProposalProvider.md) - `class ProposalProvider(Protocol)` in `application/ports` (the source has no docstring).
* [application.ports.UnitOfWork](/symbols/application/ports/UnitOfWork.md) - All mutations on this port commit together or roll back together.
* [application.runtime.execute](/symbols/application/runtime/execute.md) - `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault=None) -> dict` in `application/runtime` (the source has no d…
* [application.runtime.initialise](/symbols/application/runtime/initialise.md) - `def initialise(session: UnitOfWork, case_id: str, model: Workflow, *, state: str | None=None) -> dict` in `application/runtime` (the source has no docstring).
* [application.service.Studio.create](/symbols/application/service/Studio.create.md) - `def create(self, request: str) -> dict` in `application/service` (the source has no docstring).
* [application.verifier.verify_runtime](/symbols/application/verifier/verify_runtime.md) - `def verify_runtime(model: Workflow, subject: dict, sandbox: SandboxFactory) -> dict` in `application/verifier` (the source has no docstring).
* [domain.change_case.ChangeCase.executable](/symbols/domain/change_case/ChangeCase.executable.md) - `def executable(self) -> Workflow` in `domain/change_case` (the source has no docstring).
* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.
* [domain.impact.model_impact](/symbols/domain/impact/model_impact.md) - `def model_impact(before: Workflow, after: Workflow) -> dict` in `domain/impact` (the source has no docstring).
* [domain.models.Workflow.coherent](/symbols/domain/models/Workflow.coherent.md) - `def coherent(self) -> Workflow` in `domain/models` (the source has no docstring).
* [domain.models.Workflow.semantic_hash](/symbols/domain/models/Workflow.semantic_hash.md) - `def semantic_hash(self) -> str` in `domain/models` (the source has no docstring).
* [domain.policy.apply_transaction](/symbols/domain/policy/apply_transaction.md) - `def apply_transaction(model: Workflow, tx: SemanticTransaction) -> Workflow` in `domain/policy` (the source has no docstring).
* [domain.policy.baseline](/symbols/domain/policy/baseline.md) - `def baseline() -> Workflow` in `domain/policy` (the source has no docstring).
* [domain.policy.check_policy](/symbols/domain/policy/check_policy.md) - `def check_policy(model: Workflow) -> list[str]` in `domain/policy` (the source has no docstring).
* [domain.policy.ensure_policy](/symbols/domain/policy/ensure_policy.md) - `def ensure_policy(model: Workflow) -> None` in `domain/policy` (the source has no docstring).
* [domain.policy.meaning_questions](/symbols/domain/policy/meaning_questions.md) - `def meaning_questions(model: Workflow) -> list[dict]` in `domain/policy` (the source has no docstring).
* [domain.policy.projections](/symbols/domain/policy/projections.md) - Journey wording and rules derive from executable transitions, not AI copy.
<!-- okf:generated:end links -->
