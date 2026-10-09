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
  sha256: 25d08a237e7219fa29833d234f86b1a8c96b0590958e42ea12c8a0ec2e0614f0
notes_baseline: 12fe6c4b1de3f8a4e17e98b82fc7aee91a3dd392470d09258ebc9a036aacaca7
---

# application.plan.propose_plan

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/plan`](/modules/application/plan.md) |
| Signature | `def propose_plan(request: str, model: Workflow, pack: Pack, proposer: PlanProposer, grows: bool=False) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/plan.py#propose_plan` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Ask the proposer for a plan, re-check it, and preview it with every step accepted. `model` may already carry
earlier rounds of the same work in progress (ADR-0201): the new steps are planned on top of it. When the system
`grows`, the proposer may name new states, actions and roles, and the preview declares them.
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

## Referenced by

* [application.plan.example_passes](/symbols/application/plan/example_passes.md) - Whether `request`, sent to the chat as it stands, becomes a plan the policy allows on `model`.
<!-- okf:generated:end links -->
