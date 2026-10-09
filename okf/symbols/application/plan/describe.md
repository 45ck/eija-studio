---
type: Function
title: application.plan.describe
description: One line a person can check against the diagram.
resource: repo://src/eija_studio/application/plan.py#describe
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/plan.py#describe
  title: application/plan.py
  hash_method: ast-v2
  sha256: 6fe93f102e2fe149b109e8b09dc8b414685bdf361271d00b8f5b89ff5f6e4350
notes_baseline: ff5c9e38bc47cda1e68b16737edbaabb80efe961489b53b7aadf9432ef94a7cc
---

# application.plan.describe

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/plan`](/modules/application/plan.md) |
| Signature | `def describe(tx: Step, model: Workflow \| None=None, pack: Pack \| None=None, plan: list[Step] \| None=None) -> str` |
| Code | `repo://src/eija_studio/application/plan.py#describe` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
One line a person can check against the diagram. A transition is named by its action, as the diagram labels it,
when `model` has it or a step of the same `plan` adds it. An action or role `pack` does not declare yet is
called new, so a person sees when a step grows the system's vocabulary (ADR-0201). A data-model step reads as the
class diagram says it (ADR-0202).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.data_steps.DATA_EDITS](/symbols/application/data_steps/DATA_EDITS.md) - Constant `DATA_EDITS` in `application/data_steps`.
* [application.data_steps.Step](/symbols/application/data_steps/Step.md) - Type alias `Step` in `application/data_steps`.
* [application.data_steps.describe_data](/symbols/application/data_steps/describe_data.md) - One line a person can check against the class diagram.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.transactions.AddTransition](/symbols/domain/transactions/AddTransition.md) - A transition performing a declared action; its guards and effects are the action's declared ones.

## Referenced by

* [application.plan.propose_plan](/symbols/application/plan/propose_plan.md) - Ask the proposer for a plan, re-check it, and preview it with every step accepted.
<!-- okf:generated:end links -->
