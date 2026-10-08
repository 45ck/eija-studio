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
  sha256: b7d83ecd43b3669c7c7cdc0707d7f45818c6f1d080c27d1439a32e5203a0c2bd
notes_baseline: 6255679d46286a6eea390e0dd3119fa3d3931c8c9c20706f86555f1092328c90
---

# application.plan.describe

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/plan`](/modules/application/plan.md) |
| Signature | `def describe(tx: Transaction) -> str` |
| Code | `repo://src/eija_studio/application/plan.py#describe` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
One line a person can check against the diagram.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.

## Referenced by

* [application.plan.propose_plan](/symbols/application/plan/propose_plan.md) - Ask the proposer for a plan, re-check it, and preview it with every step accepted.
<!-- okf:generated:end links -->
