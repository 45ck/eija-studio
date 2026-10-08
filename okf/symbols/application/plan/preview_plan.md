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
  sha256: d5ad19463f416424477796228b79ac05d9febf355a657c8c2d4ad7041da49944
notes_baseline: 7b466d21f5f65da4ef66d6981d4b66d7ce508c1a8fb83c47d5e5613d5a3d5660
---

# application.plan.preview_plan

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/plan`](/modules/application/plan.md) |
| Signature | `def preview_plan(model: Workflow, pack: Pack, transactions: list[Transaction], accepted: list[bool]) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/plan.py#preview_plan` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
What the accepted steps would make of `model`. Each step reports whether it applies after the accepted ones
before it; the accepted steps together are then checked against the policy as one change.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.diagrams.diff_summary](/symbols/application/diagrams/diff_summary.md) - Structured diff of two workflows: states, and transitions by action with each changed field's before and after.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.policy.apply_transactions](/symbols/domain/policy/apply_transactions.md) - Apply an edit sequence as one change: the start must conform, the result must conform (intermediate steps need only be coherent workflows).
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.

## Referenced by

* [application.plan.propose_plan](/symbols/application/plan/propose_plan.md) - Ask the proposer for a plan, re-check it, and preview it with every step accepted.
<!-- okf:generated:end links -->
