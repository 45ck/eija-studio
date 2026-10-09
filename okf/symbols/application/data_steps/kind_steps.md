---
type: Function
title: application.data_steps.kind_steps
description: The role-kind steps, in plan order.
resource: repo://src/eija_studio/application/data_steps.py#kind_steps
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/data_steps.py#kind_steps
  title: application/data_steps.py
  hash_method: ast-v2
  sha256: b6e2242538d324113aa6a242a32ceb67b0f4225c804d65fc9e3df48d6086f50e
notes_baseline: 58fd48ed237f4d17878c45dcebb3e45ddcccaaf68f43bb2d628a06422f1a30f2
---

# application.data_steps.kind_steps

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/data_steps`](/modules/application/data_steps.md) |
| Signature | `def kind_steps(steps: Sequence[Step]) -> list[SetRoleKind]` |
| Code | `repo://src/eija_studio/application/data_steps.py#kind_steps` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The role-kind steps, in plan order.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.data_steps.SetRoleKind](/symbols/application/data_steps/SetRoleKind.md) - Make the actor holding `role` a person, an AI agent, a timer or an external system (ADR-0210).
* [application.data_steps.Step](/symbols/application/data_steps/Step.md) - Type alias `Step` in `application/data_steps`.

## Referenced by

* [application.data_steps.draft_pack](/symbols/application/data_steps/draft_pack.md) - `pack` as these plan steps would have it, held in memory: on a system the person started (`grows`), the actions and roles they name are declared (ADR-0201) and…
* [application.plan.preview_plan](/symbols/application/plan/preview_plan.md) - What the accepted steps would make of `model`.
<!-- okf:generated:end links -->
