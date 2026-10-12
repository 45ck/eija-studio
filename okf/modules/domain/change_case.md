---
type: Module
title: domain.change_case
description: Module `domain/change_case` (no module docstring).
resource: repo://src/eija_studio/domain/change_case.py
tags:
- module
- domain
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/change_case.py
  title: domain/change_case.py
  hash_method: ast-api-v1
  sha256: 3aaa2b8cd16f34c15ec6e630e214e55abff947e07945c121c357e28f05083427
notes_baseline: 3df10055b2f80388f37db937779eb8e1490a5368aeecd932d5e793fc541387e9
---

# domain.change_case

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | domain |
| Code | `repo://src/eija_studio/domain/change_case.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

_The source carries no module docstring._

## Public symbols

* [`ChangeCase`](/symbols/domain/change_case/ChangeCase.md) (class) - Aggregate boundary: transitions are mediated by the application and CAS store.
* [`OwnerPlanRequest`](/symbols/domain/change_case/OwnerPlanRequest.md) (class) - Exact accepted workflow commands and the identities of their reviewed preview.
* [`OwnerPlanSelection`](/symbols/domain/change_case/OwnerPlanSelection.md) (class) - no docstring
* [`OwnerPlanStep`](/symbols/domain/change_case/OwnerPlanStep.md) (class) - Reported proposal provenance, never a capability or an owner decision.
* [`PackMeaningSelection`](/symbols/domain/change_case/PackMeaningSelection.md) (class) - no docstring
* [`Selection`](/symbols/domain/change_case/Selection.md) (type-alias) - no docstring

## Internal imports

* [`domain/generated_app`](/modules/domain/generated_app.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/transactions`](/modules/domain/transactions.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.generated_app](/modules/domain/generated_app.md) - Versioned exact generated-app selection and evidence contracts; no authority is implied by a hash.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.transactions](/modules/domain/transactions.md) - Open change vocabulary (WBS 1.3): the semantic edits an owner (or a pack meaning) may make to a workflow.

## Referenced by

* [Authoring](/contexts/authoring.md) - Owns Requested intent, alternatives, explicit selection, candidate and edits
* [application.compiler](/modules/application/compiler.md) - Compiler: model → projections + impacts + obligations + computed review packet.
* [application.diagrams](/modules/application/diagrams.md) - Diagram models derived from the executable Workflow (ADR-0019, ADR-0023).
* [application.edit_preview](/modules/application/edit_preview.md) - Read-only edit projection over one captured case, using the same interpreter as owner edits.
* [application.edit_proposal](/modules/application/edit_proposal.md) - A read-only offline proposal over one captured candidate; owner edits keep their existing boundary.
* [application.generated_app](/modules/application/generated_app.md) - Shared generation and exact-app evidence operations for the existing kernel and checker.
* [application.history](/modules/application/history.md) - Semantic history is a projection of typed commands, replayed by the existing policy interpreter.
* [application.owner_plan](/modules/application/owner_plan.md) - Exact owner-plan case construction; authority and atomic storage remain in Studio.
* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
* [application.service_views](/modules/application/service_views.md) - Read-only Studio projections over the same case, pack and exact-app evidence.
* [interfaces.http](/modules/interfaces/http.md) - Loopback-only local adapter.
* [domain.change_case.ChangeCase.at_version](/symbols/domain/change_case/ChangeCase.at_version.md) - `def at_version(self, expected: int) -> None` in `domain/change_case`.
* [domain.change_case.ChangeCase.executable](/symbols/domain/change_case/ChangeCase.executable.md) - `def executable(self) -> Workflow` in `domain/change_case`.
* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.
* [domain.change_case.ChangeCase.require_editable](/symbols/domain/change_case/ChangeCase.require_editable.md) - `def require_editable(self) -> None` in `domain/change_case`.
* [domain.change_case.OwnerPlanRequest](/symbols/domain/change_case/OwnerPlanRequest.md) - Exact accepted workflow commands and the identities of their reviewed preview.
* [domain.change_case.OwnerPlanSelection](/symbols/domain/change_case/OwnerPlanSelection.md) - `class OwnerPlanSelection(Contract)` in `domain/change_case`.
* [domain.change_case.OwnerPlanStep](/symbols/domain/change_case/OwnerPlanStep.md) - Reported proposal provenance, never a capability or an owner decision.
* [domain.change_case.PackMeaningSelection](/symbols/domain/change_case/PackMeaningSelection.md) - `class PackMeaningSelection(Contract)` in `domain/change_case`.
* [domain.change_case.Selection](/symbols/domain/change_case/Selection.md) - Type alias `Selection` in `domain/change_case`.
<!-- okf:generated:end links -->
