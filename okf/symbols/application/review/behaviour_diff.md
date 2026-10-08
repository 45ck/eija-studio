---
type: Function
title: application.review.behaviour_diff
description: Every fixture actor tries every action from every state on both models; the attempts whose outcome differs.
resource: repo://src/eija_studio/application/review.py#behaviour_diff
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/review.py#behaviour_diff
  title: application/review.py
  hash_method: ast-v2
  sha256: c456abd2980393de4161f788d25603967873fe416479c4c378918393129768fa
notes_baseline: 8cb94110c947ae84af0909c5257941219deaf74a35bf9eeba7d4f85373f42df9
---

# application.review.behaviour_diff

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/review`](/modules/application/review.md) |
| Signature | `def behaviour_diff(pack: Pack, before: Workflow, after: Workflow) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/review.py#behaviour_diff` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Every fixture actor tries every action from every state on both models; the attempts whose outcome differs.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.review.review_change](/symbols/application/review/review_change.md) - Everything a reviewer needs to check a change: what changed, how risky, and what the kernel does differently.
<!-- okf:generated:end links -->
