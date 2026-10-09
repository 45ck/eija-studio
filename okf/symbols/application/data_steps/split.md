---
type: Function
title: application.data_steps.split
description: The kernel transactions and the data-model steps, each in plan order (role-kind steps are in neither).
resource: repo://src/eija_studio/application/data_steps.py#split
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/data_steps.py#split
  title: application/data_steps.py
  hash_method: ast-v2
  sha256: a85d5b9244b4211119d2849fae8fdbe39fac492eaaddd5a3d52d770b47c60bd4
notes_baseline: a51b051e3c09e0c4dbf1df91d8c7fa98a77854833968cd56a61b61c887385453
---

# application.data_steps.split

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/data_steps`](/modules/application/data_steps.md) |
| Signature | `def split(steps: Sequence[Step]) -> tuple[list[Transaction], list[DataEdit]]` |
| Code | `repo://src/eija_studio/application/data_steps.py#split` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The kernel transactions and the data-model steps, each in plan order (role-kind steps are in neither).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.data_steps.DATA_EDITS](/symbols/application/data_steps/DATA_EDITS.md) - Constant `DATA_EDITS` in `application/data_steps`.
* [application.data_steps.DataEdit](/symbols/application/data_steps/DataEdit.md) - Type alias `DataEdit` in `application/data_steps`.
* [application.data_steps.SetRoleKind](/symbols/application/data_steps/SetRoleKind.md) - Make the actor holding `role` a person, an AI agent, a timer or an external system (ADR-0210).
* [application.data_steps.Step](/symbols/application/data_steps/Step.md) - Type alias `Step` in `application/data_steps`.
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.

## Referenced by

* [application.data_steps.draft_pack](/symbols/application/data_steps/draft_pack.md) - `pack` as these plan steps would have it, held in memory: on a system the person started (`grows`), the actions and roles they name are declared (ADR-0201) and…
* [application.plan.preview_plan](/symbols/application/plan/preview_plan.md) - What the accepted steps would make of `model`.
* [application.ripple.check_follow_ons](/symbols/application/ripple/check_follow_ons.md) - The proposer's follow-on steps, each re-checked on its own on top of the plan: a state-machine step through the policy (`base` with `plan` and the step), a scr…
<!-- okf:generated:end links -->
