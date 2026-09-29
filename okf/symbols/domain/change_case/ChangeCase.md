---
type: Class
title: domain.change_case.ChangeCase
description: Aggregate linking one request to its interpretations, chosen meaning, baseline, candidate, transactions, receipts and decision.
resource: repo://src/eija_studio/domain/change_case.py#ChangeCase
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/change_case.py#ChangeCase
  title: domain/change_case.py
  hash_method: ast-sig-v1
  sha256: 000e4f2582dbd14bcba5851ae3e3e3b76e09f62af8532c945821e32d7896ac58
description_override: Aggregate linking one request to its interpretations, chosen meaning, baseline, candidate, transactions, receipts and decision.
notes_baseline: e5d1c0fc9a15557a6db9b580b3e19cff6b4b45293fdcfa3f67e0e0e16b15c02f
---

# domain.change_case.ChangeCase

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/change_case`](/modules/domain/change_case.md) |
| Signature | `class ChangeCase(Contract)` |
| Code | `repo://src/eija_studio/domain/change_case.py#ChangeCase` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Aggregate boundary: transitions are mediated by the application and CAS store.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `id` | `str` |  |
| `version` | `int` |  |
| `stage` | `Literal['DRAFT', 'PROPOSED', 'PREVIEW', 'SAVED', 'VERIFIED', 'APPROVED', 'APPLIED', 'DISCARDED']` |  |
| `request` | `str` |  |
| `baseline_version` | `int` |  |
| `baseline` | `Workflow` |  |
| `candidate` | `Workflow \| None` |  |
| `proposal` | `Proposal \| None` |  |
| `provider_run` | `dict[str, Any] \| None` |  |
| `selected_meaning` | `str \| None` |  |
| `selected_by` | `str \| None` |  |
| `transactions` | `tuple[SemanticTransaction, ...]` |  |
| `layout` | `dict[str, dict[str, int]]` |  |
| `receipts` | `tuple[dict[str, Any], ...]` |  |
| `decision` | `dict[str, Any] \| None` |  |
| `created_at` | `str` |  |

## Methods

* [`at_version`](/symbols/domain/change_case/ChangeCase.at_version.md) - `def at_version(self, expected: int) -> None`
* [`executable`](/symbols/domain/change_case/ChangeCase.executable.md) - `def executable(self) -> Workflow`
* [`require_editable`](/symbols/domain/change_case/ChangeCase.require_editable.md) - `def require_editable(self) -> None`
<!-- okf:generated:end facts -->

## Notes

The aggregate behind [Change Case](/language/change-case.md). Its `version` is a compare-and-swap counter distinct from an instance version. Stage never grants eligibility on its own: [compile_case](/symbols/application/compiler/compile_case.md) computes it. `APPLIED` and `DISCARDED` cases are closed ([require_editable](/symbols/domain/change_case/ChangeCase.require_editable.md)).

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.models.Proposal](/symbols/domain/models/Proposal.md) - `class Proposal(Contract)` in `domain/models`.
* [domain.models.SemanticTransaction](/symbols/domain/models/SemanticTransaction.md) - `class SemanticTransaction(Contract)` in `domain/models`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [Authoring](/contexts/authoring.md) - Owns Requested intent, alternatives, explicit selection, candidate and edits
* [Change Case](/language/change-case.md) - Aggregate linking one original request to interpretations, chosen meaning, baseline, candidate, transactions, receipts and decision.
* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],…` in `application/compiler`.
* [application.diagrams.CONTRACTS](/symbols/application/diagrams/CONTRACTS.md) - Constant `CONTRACTS` in `application/diagrams`.
* [application.service.Studio.create](/symbols/application/service/Studio.create.md) - `def create(self, request: str) -> dict[str, Any]` in `application/service`.
* [domain.change_case.ChangeCase.at_version](/symbols/domain/change_case/ChangeCase.at_version.md) - `def at_version(self, expected: int) -> None` in `domain/change_case`.
* [domain.change_case.ChangeCase.executable](/symbols/domain/change_case/ChangeCase.executable.md) - `def executable(self) -> Workflow` in `domain/change_case`.
* [domain.change_case.ChangeCase.require_editable](/symbols/domain/change_case/ChangeCase.require_editable.md) - `def require_editable(self) -> None` in `domain/change_case`.
<!-- okf:generated:end links -->
