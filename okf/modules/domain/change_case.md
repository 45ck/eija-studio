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
  sha256: abca088cbf899205a08b470e144b2bd053cb25400cb5cd6e7ff5b5817e65fc12
notes_baseline: b18e6529849821eb0a9ae679a1ed96d3dcc3510c2ac2560861331744e771a4a7
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

* [`domain/models`](/modules/domain/models.md)
* [`domain/transactions`](/modules/domain/transactions.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.transactions](/modules/domain/transactions.md) - Open change vocabulary (WBS 1.3): the semantic edits an owner (or a pack meaning) may make to a workflow.

## Referenced by

* [Authoring](/contexts/authoring.md) - Owns Requested intent, alternatives, explicit selection, candidate and edits
* [application.compiler](/modules/application/compiler.md) - Compiler: model → projections + impacts + obligations + computed review packet.
* [application.diagrams](/modules/application/diagrams.md) - Diagram models derived from the executable Workflow (ADR-0019, ADR-0023).
* [application.edit_preview](/modules/application/edit_preview.md) - Read-only edit projection over one captured case, using the same interpreter as owner edits.
* [application.edit_proposal](/modules/application/edit_proposal.md) - A read-only offline proposal over one captured candidate; owner edits keep their existing boundary.
* [application.history](/modules/application/history.md) - Semantic history is a projection of typed commands, replayed by the existing policy interpreter.
* [application.owner_plan](/modules/application/owner_plan.md) - Exact owner-plan case construction; authority and atomic storage remain in Studio.
* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
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
