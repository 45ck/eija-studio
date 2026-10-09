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
  sha256: e392368459c49799262ac4514728c7e6acca2b7d94fb06bc6725155cf298689d
notes_baseline: 5bbf041ec629fe2ed6bc157744f6e4f968d051da8bb22bc92e7b3baa86850b2b
---

# application.plan.describe

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/plan`](/modules/application/plan.md) |
| Signature | `def describe(tx: Transaction, model: Workflow \| None=None, pack: Pack \| None=None, plan: list[Transaction] \| None=None) -> str` |
| Code | `repo://src/eija_studio/application/plan.py#describe` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
One line a person can check against the diagram. A transition is named by its action, as the diagram labels it,
when `model` has it or a step of the same `plan` adds it. An action or role `pack` does not declare yet is
called new, so a person sees when a step grows the system's vocabulary (ADR-0201).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.transactions.AddTransition](/symbols/domain/transactions/AddTransition.md) - A transition performing a declared action; its guards and effects are the action's declared ones.
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.

## Referenced by

* [application.plan.propose_plan](/symbols/application/plan/propose_plan.md) - Ask the proposer for a plan, re-check it, and preview it with every step accepted.
<!-- okf:generated:end links -->
