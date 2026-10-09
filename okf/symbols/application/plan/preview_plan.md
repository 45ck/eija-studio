---
type: Function
title: application.plan.preview_plan
description: What the accepted steps would make of `model`.
resource: repo://src/eija_studio/application/plan.py#preview_plan
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/plan.py#preview_plan
  title: application/plan.py
  hash_method: ast-v2
  sha256: fbfc2bb5733d0c20a643fd921cc9614eccb340d3a436c75d5b270d2c3a93ec40
notes_baseline: 0fae4f95bc8ead001d1cc82c60f9340a6fa2e27f9fea0fc6f3c1fd16e73d58b9
---

# application.plan.preview_plan

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/plan`](/modules/application/plan.md) |
| Signature | `def preview_plan(model: Workflow, pack: Pack, transactions: list[Step], accepted: list[bool], grows: bool=False) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/plan.py#preview_plan` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
What the accepted steps would make of `model`. Each step reports whether it applies after the accepted ones
before it; the accepted steps together are then checked against the policy as one change. When the system `grows`
(one you started, ADR-0201), an action or role the accepted steps name is declared as a sketch declares it, and its
data-model steps change a draft of its class diagram (ADR-0202): `data` is that draft and `data_changes` what changed.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.data_steps.Step](/symbols/application/data_steps/Step.md) - Type alias `Step` in `application/data_steps`.
* [application.data_steps.draft_pack](/symbols/application/data_steps/draft_pack.md) - `pack` as these plan steps would have it, held in memory: on a system the person started (`grows`), the actions and roles they name are declared (ADR-0201) and…
* [application.data_steps.is_data](/symbols/application/data_steps/is_data.md) - `def is_data(step: Step) -> bool` in `application/data_steps`.
* [application.data_steps.split](/symbols/application/data_steps/split.md) - The kernel transactions and the data-model steps, each in plan order.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.plan.propose_plan](/symbols/application/plan/propose_plan.md) - Ask the proposer for a plan, re-check it, and preview it with every step accepted.
<!-- okf:generated:end links -->
