---
type: Function
title: application.review.review_change
description: 'Everything a reviewer needs to check a change: what changed, how risky, and what the kernel does differently.'
resource: repo://src/eija_studio/application/review.py#review_change
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/review.py#review_change
  title: application/review.py
  hash_method: ast-v2
  sha256: 800112348b7f09178f9a3786e28ed7f8b26d7c83d4511f3a178bac1dd22bc19f
notes_baseline: 756710b683127f83f14512c39e6db1f9ead0420de0239c8b5616276a97dcdf44
---

# application.review.review_change

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/review`](/modules/application/review.md) |
| Signature | `def review_change(pack: Pack, before: Workflow, after: Workflow) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/review.py#review_change` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Everything a reviewer needs to check a change: what changed, how risky, and what the kernel does differently.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.diagrams.diff_summary](/symbols/application/diagrams/diff_summary.md) - Structured diff of two workflows: states, and transitions by action with each changed field's before and after.
* [application.review.RISK_ORDER](/symbols/application/review/RISK_ORDER.md) - Constant `RISK_ORDER` in `application/review`.
* [application.review.behaviour_diff](/symbols/application/review/behaviour_diff.md) - Every fixture actor tries every action from every state on both models; the attempts whose outcome differs.
* [application.review.renames](/symbols/application/review/renames.md) - States the change renamed: a state that is gone, matched to the one new state that every transition and the start that used it now use instead (counting only t…
* [application.review.row_text](/symbols/application/review/row_text.md) - `def row_text(row: dict[str, Any]) -> str` in `application/review`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
