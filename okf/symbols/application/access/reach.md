---
type: Function
title: application.access.reach
description: Can a record reach `target` with no step taken by role `without` (or at all, when it is None)?
resource: repo://src/eija_studio/application/access.py#reach
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/access.py#reach
  title: application/access.py
  hash_method: ast-v2
  sha256: c8ab577e86d9e70f8f0821480e7889e5150abb669d54e81715ace7024685ccba
notes_baseline: 5b201b1971c95627e5768e17ee9fe4275dcf1d69ac3a2a5cf507cbf03fab0db9
---

# application.access.reach

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/access`](/modules/application/access.md) |
| Signature | `def reach(pack: Pack, model: Workflow, target: str, without: str \| None=None) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/access.py#reach` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Can a record reach `target` with no step taken by role `without` (or at all, when it is None)?
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
