---
type: Function
title: application.review.renames
description: 'States the change renamed: a state that is gone, matched to the one new state that every transition and the start that used it now use instead (counting only transitions on both sides, and with nothing else moved onto i…'
resource: repo://src/eija_studio/application/review.py#renames
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/review.py#renames
  title: application/review.py
  hash_method: ast-v2
  sha256: 77751f816924d0815a72258f5d8de313dd6c70dfb2ea5b1b65fda8a0ad8e2072
notes_baseline: e322ab2b85b1edc9cbea1138c0eee5f4c99d1c09c7768bd1586bf32f182db07f
---

# application.review.renames

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/review`](/modules/application/review.md) |
| Signature | `def renames(before: Workflow, after: Workflow) -> dict[str, str]` |
| Code | `repo://src/eija_studio/application/review.py#renames` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
States the change renamed: a state that is gone, matched to the one new state that every transition and the
start that used it now use instead (counting only transitions on both sides, and with nothing else moved onto it).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [application.review.review_change](/symbols/application/review/review_change.md) - Everything a reviewer needs to check a change: what changed, how risky, and what the kernel does differently.
<!-- okf:generated:end links -->
