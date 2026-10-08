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
  sha256: d66ce7cd9609d2743151b14133faf312859e00342237230381813d62e4dd899b
notes_baseline: 04151ff06c0314e4ff6e2275f727942c24287b7508ad570c4ec7ba5ce2ad6859
---

# application.plan.describe

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/plan`](/modules/application/plan.md) |
| Signature | `def describe(tx: Transaction, model: Workflow \| None=None) -> str` |
| Code | `repo://src/eija_studio/application/plan.py#describe` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
One line a person can check against the diagram. A transition is named by its action, as the diagram labels it,
when `model` has it; one the same plan adds keeps its id.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.

## Referenced by

* [application.plan.propose_plan](/symbols/application/plan/propose_plan.md) - Ask the proposer for a plan, re-check it, and preview it with every step accepted.
<!-- okf:generated:end links -->
