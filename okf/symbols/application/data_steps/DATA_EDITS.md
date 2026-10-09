---
type: Constant
title: application.data_steps.DATA_EDITS
description: Constant `DATA_EDITS` in `application/data_steps`.
resource: repo://src/eija_studio/application/data_steps.py#DATA_EDITS
tags:
- symbol
- application
- constant
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/data_steps.py#DATA_EDITS
  title: application/data_steps.py
  hash_method: ast-v2
  sha256: 6ca902b5438957dd5d32b4189e4963fd6b7d6aafda22684ed1e2ee0619801434
notes_baseline: 2b079da3193aa1a1bc4cac3b71748ab7bde884cebcafab6e6a75c08688685457
---

# application.data_steps.DATA_EDITS

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`application/data_steps`](/modules/application/data_steps.md) |
| Signature | `DATA_EDITS = (AddAttribute, RemoveAttribute, SetRequired, SetRoleKind)` |
| Code | `repo://src/eija_studio/application/data_steps.py#DATA_EDITS` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.data_steps.AddAttribute](/symbols/application/data_steps/AddAttribute.md) - `class AddAttribute(Contract)` in `application/data_steps`.
* [application.data_steps.RemoveAttribute](/symbols/application/data_steps/RemoveAttribute.md) - `class RemoveAttribute(Contract)` in `application/data_steps`.
* [application.data_steps.SetRequired](/symbols/application/data_steps/SetRequired.md) - `class SetRequired(Contract)` in `application/data_steps`.
* [application.data_steps.SetRoleKind](/symbols/application/data_steps/SetRoleKind.md) - `class SetRoleKind(Contract)` in `application/data_steps`.

## Referenced by

* [application.data_steps.is_data](/symbols/application/data_steps/is_data.md) - `def is_data(step: Step) -> bool` in `application/data_steps`.
* [application.data_steps.split](/symbols/application/data_steps/split.md) - The kernel transactions and the data-model steps, each in plan order.
* [application.plan.describe](/symbols/application/plan/describe.md) - One line a person can check against the diagram.
<!-- okf:generated:end links -->
