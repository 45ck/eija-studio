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
  sha256: 2f9345ec89e88175f10c4c471f2cbe3fba78271a0154a83004858093a914fb8d
notes_baseline: ca065172356aeebb7ebed8657f1a9b2eb5f240d7927a3289faae01335d00b92b
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
* [application.review.row_text](/symbols/application/review/row_text.md) - `def row_text(row: dict[str, Any]) -> str` in `application/review`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
