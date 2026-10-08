---
type: Function
title: application.plan.propose_plan
description: Ask the proposer for a plan, re-check it, and preview it with every step accepted.
resource: repo://src/eija_studio/application/plan.py#propose_plan
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/plan.py#propose_plan
  title: application/plan.py
  hash_method: ast-v2
  sha256: ee3a76b106fcd1b03f10b306355f8b7b486bc39e6072fcf4900d97095960d788
notes_baseline: 383e4f2da887885f137fbd74dd34b0f386eea965a1f9b51da4e5594da06a46a8
---

# application.plan.propose_plan

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/plan`](/modules/application/plan.md) |
| Signature | `def propose_plan(request: str, model: Workflow, pack: Pack, proposer: PlanProposer) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/plan.py#propose_plan` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Ask the proposer for a plan, re-check it, and preview it with every step accepted.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.plan.MAX_REQUEST](/symbols/application/plan/MAX_REQUEST.md) - Constant `MAX_REQUEST` in `application/plan`.
* [application.plan.describe](/symbols/application/plan/describe.md) - One line a person can check against the diagram.
* [application.plan.preview_plan](/symbols/application/plan/preview_plan.md) - What the accepted steps would make of `model`.
* [application.ports.PlanProposer](/symbols/application/ports/PlanProposer.md) - Turns a chat request into {summary, meaning, steps: [{transaction, why}]}.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
