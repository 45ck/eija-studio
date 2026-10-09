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
  sha256: 09275356c73393ddc029c606f3e3c627a833076f59966795d1914c30c6c4c852
notes_baseline: df927ed229cb91af33e34a0f987898404c84853dfafc59575e0d34985277f9e5
---

# application.data_steps.DATA_EDITS

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`application/data_steps`](/modules/application/data_steps.md) |
| Signature | `DATA_EDITS = (AddAttribute, RemoveAttribute, SetRequired)` |
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

## Referenced by

* [application.data_steps.is_data](/symbols/application/data_steps/is_data.md) - `def is_data(step: Step) -> bool` in `application/data_steps`.
* [application.data_steps.split](/symbols/application/data_steps/split.md) - The kernel transactions and the data-model steps, each in plan order.
* [application.plan.describe](/symbols/application/plan/describe.md) - One line a person can check against the diagram.
<!-- okf:generated:end links -->
