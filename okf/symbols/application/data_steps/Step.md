---
type: Type Alias
title: application.data_steps.Step
description: Type alias `Step` in `application/data_steps`.
resource: repo://src/eija_studio/application/data_steps.py#Step
tags:
- symbol
- application
- type-alias
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/data_steps.py#Step
  title: application/data_steps.py
  hash_method: ast-v2
  sha256: 5c0ffc1bf4f1c79c173bd81910a0238de8c404da8c417c0fde2842b9b9ef76ca
notes_baseline: 8e8ff2c938f2c303a5a7685295470c28921ea3ca54c336610a82a3783a528161
---

# application.data_steps.Step

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | type-alias |
| Module | [`application/data_steps`](/modules/application/data_steps.md) |
| Signature | `Step = Transaction \| DataEdit` |
| Code | `repo://src/eija_studio/application/data_steps.py#Step` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.data_steps.DataEdit](/symbols/application/data_steps/DataEdit.md) - Type alias `DataEdit` in `application/data_steps`.
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.

## Referenced by

* [application.data_steps.draft_pack](/symbols/application/data_steps/draft_pack.md) - `pack` as these plan steps would have it, held in memory: on a system the person started (`grows`), the actions and roles they name are declared (ADR-0201) and…
* [application.data_steps.is_data](/symbols/application/data_steps/is_data.md) - `def is_data(step: Step) -> bool` in `application/data_steps`.
* [application.data_steps.parse_step](/symbols/application/data_steps/parse_step.md) - A plan step: a data-model step, or else a kernel transaction (`parse_transaction`).
* [application.data_steps.split](/symbols/application/data_steps/split.md) - The kernel transactions and the data-model steps, each in plan order.
* [application.plan.describe](/symbols/application/plan/describe.md) - One line a person can check against the diagram.
* [application.plan.preview_plan](/symbols/application/plan/preview_plan.md) - What the accepted steps would make of `model`.
<!-- okf:generated:end links -->
