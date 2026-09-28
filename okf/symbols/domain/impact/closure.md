---
type: Function
title: domain.impact.closure
description: Fixed-point, cycle-safe reachability over a dependency graph; a budget yields complete=false and an explicit frontier, never a silent cap.
resource: repo://src/eija_studio/domain/impact.py#closure
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/impact.py#closure
  title: domain/impact.py
  hash_method: ast-v1
  sha256: 0dcfd83e15e63b18ec3d2f12098d3de35eb45bdfabe0e3642b6333503d324eec
description_override: Fixed-point, cycle-safe reachability over a dependency graph; a budget yields complete=false and an explicit frontier, never a silent cap.
---

# domain.impact.closure

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/impact`](/modules/domain/impact.md) |
| Signature | `def closure(graph: dict[str, list[str]], roots: list[str], budget: int \| None=None) -> dict` |
| Code | `repo://src/eija_studio/domain/impact.py#closure` |
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

~~~text
Edges mean source affects target. Fixed point, cycle-safe; no silent depth cap.
~~~
<!-- okf:generated:end facts -->

## Notes

Edges mean *source affects target*. Roots are sorted and the queue visits sorted neighbours, so the result is deterministic. With a budget it returns the unvisited `frontier`; callers must treat `complete=false` as unknown, not as small impact (acceptance [AC16](/requirements/ac16.md)).

<!-- okf:generated:begin links -->
## Referenced by

* [domain.impact.model_impact](/symbols/domain/impact/model_impact.md) - `def model_impact(before: Workflow, after: Workflow) -> dict` in `domain/impact` (the source has no docstring).
<!-- okf:generated:end links -->
