---
type: Constant
title: application.diagrams.CONTRACTS
description: Constant `CONTRACTS` in `application/diagrams`.
resource: repo://src/eija_studio/application/diagrams.py#CONTRACTS
tags:
- symbol
- application
- constant
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagrams.py#CONTRACTS
  title: application/diagrams.py
  hash_method: ast-v2
  sha256: f6a5aef3fd72996f499ff9a8ca8cc255f625668411cc450ea1d7314a2939a022
notes_baseline: 52ae58f1774dc3c14d055ec354382dd23c666400f4409ca5e51921fd2ebbf875
---

# application.diagrams.CONTRACTS

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`application/diagrams`](/modules/application/diagrams.md) |
| Signature | `CONTRACTS: tuple[type[BaseModel], ...] = (ChangeCase, Workflow, Transition, Proposal, Alternative, LayoutChange, ExecuteCommand, Principal)` |
| Code | `repo://src/eija_studio/application/diagrams.py#CONTRACTS` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.
* [domain.models.Alternative](/symbols/domain/models/Alternative.md) - `class Alternative(Contract)` in `domain/models`.
* [domain.models.ExecuteCommand](/symbols/domain/models/ExecuteCommand.md) - `class ExecuteCommand(Contract)` in `domain/models`.
* [domain.models.LayoutChange](/symbols/domain/models/LayoutChange.md) - `class LayoutChange(Contract)` in `domain/models`.
* [domain.models.Principal](/symbols/domain/models/Principal.md) - `class Principal(Contract)` in `domain/models`.
* [domain.models.Proposal](/symbols/domain/models/Proposal.md) - `class Proposal(Contract)` in `domain/models`.
* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [application.diagrams.class_model](/symbols/application/diagrams/class_model.md) - Domain contracts introspected from the Pydantic models.
<!-- okf:generated:end links -->
