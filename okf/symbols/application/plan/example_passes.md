---
type: Function
title: application.plan.example_passes
description: Whether `request`, sent to the chat as it stands, becomes a plan the policy allows on `model`.
resource: repo://src/eija_studio/application/plan.py#example_passes
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/plan.py#example_passes
  title: application/plan.py
  hash_method: ast-v2
  sha256: 73dacf065c628ad611fb99bc312d832bbb0614e253b39e174569ac1d11ab1d07
notes_baseline: 88ddae1fd93108aa19e169ce4223aee537cae6b1cc8c275cc66d1a826d7344f9
---

# application.plan.example_passes

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/plan`](/modules/application/plan.md) |
| Signature | `def example_passes(request: str, model: Workflow, pack: Pack, proposer: PlanProposer \| None) -> bool` |
| Code | `repo://src/eija_studio/application/plan.py#example_passes` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Whether `request`, sent to the chat as it stands, becomes a plan the policy allows on `model`. Only an offline
proposer is asked: a live one would spend a model call on every page load, so it gets typed steps instead.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.plan.propose_plan](/symbols/application/plan/propose_plan.md) - Ask the proposer for a plan, re-check it, and preview it with every step accepted.
* [application.ports.PlanProposer](/symbols/application/ports/PlanProposer.md) - Turns a chat request into {summary, meaning, steps: [{transaction, why}]}.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
