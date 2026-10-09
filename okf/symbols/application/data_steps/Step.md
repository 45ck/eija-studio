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
  sha256: 9add6dbc07077b875bd456cc5e0827a73dfd7ce341da76e8f5846db23a9a9122
notes_baseline: b81eeffed7ce3f4fb7f3b07f071e463948d6e48c7672c10ca43089ccb8a99382
---

# application.data_steps.Step

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | type-alias |
| Module | [`application/data_steps`](/modules/application/data_steps.md) |
| Signature | `Step = Transaction \| DataEdit \| SetRoleKind` |
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
* [application.data_steps.SetRoleKind](/symbols/application/data_steps/SetRoleKind.md) - Make the actor holding `role` a person, an AI agent, a timer or an external system (ADR-0210).
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.

## Referenced by

* [application.data_steps.draft_pack](/symbols/application/data_steps/draft_pack.md) - `pack` as these plan steps would have it, held in memory: on a system the person started (`grows`), the actions and roles they name are declared (ADR-0201) and…
* [application.data_steps.is_data](/symbols/application/data_steps/is_data.md) - `def is_data(step: Step) -> bool` in `application/data_steps`.
* [application.data_steps.kind_steps](/symbols/application/data_steps/kind_steps.md) - The role-kind steps, in plan order.
* [application.data_steps.parse_step](/symbols/application/data_steps/parse_step.md) - A plan step: a data-model step, or else a kernel transaction (`parse_transaction`).
* [application.data_steps.split](/symbols/application/data_steps/split.md) - The kernel transactions and the data-model steps, each in plan order (role-kind steps are in neither).
* [application.plan.describe](/symbols/application/plan/describe.md) - One line a person can check against the diagram.
* [application.plan.preview_plan](/symbols/application/plan/preview_plan.md) - What the accepted steps would make of `model`.
<!-- okf:generated:end links -->
