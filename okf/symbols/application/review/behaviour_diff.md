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
  sha256: 920b981f6bf415bb45429734b6fc3342fa3a683badc193979e462d4dd512f57e
notes_baseline: fe3efd0b8a69b9b1ceb2b42f41d30ae5fc756b0063651a098fef4cc7eb9c955a
---

# application.review.behaviour_diff

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/review`](/modules/application/review.md) |
| Signature | `def behaviour_diff(pack: Pack, before: Workflow, after: Workflow, names: dict[str, str] \| None=None) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/review.py#behaviour_diff` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Every fixture actor tries every action from every state on both models; the attempts whose outcome differs.
A renamed state (`names`, old to new) is the same state on both sides: the kernel runs each model as it is, and a
destination is compared under its new name.
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
