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
  hash_method: ast-v2
  sha256: 5a682b85632ea65ec4c65b6f4aaf2c5923e4c654dc5496c8f586d77f6eec0143
description_override: Fixed-point, cycle-safe reachability over a dependency graph; a budget yields complete=false and an explicit frontier, never a silent cap.
notes_baseline: e4cf8f1ff509568b6cebd4f543f7e17505a234493ab0c9f4ffd3788d7d2bfe55
---

# domain.impact.closure

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/impact`](/modules/domain/impact.md) |
| Signature | `def closure(graph: dict[str, list[str]], roots: list[str], budget: int \| None=None) -> dict` |
| Code | `repo://src/eija_studio/domain/impact.py#closure` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Edges mean source affects target. Fixed point, cycle-safe; no silent depth cap.
~~~
<!-- okf:generated:end facts -->

## Notes

Edges mean *source affects target*. Roots are sorted and the queue visits sorted neighbours, so the result is deterministic. With a budget it returns the unvisited `frontier`; callers must treat `complete=false` as unknown, not as small impact (acceptance [AC16](/requirements/ac16.md)).

<!-- okf:generated:begin links -->
## Referenced by

* [domain.impact.model_impact](/symbols/domain/impact/model_impact.md) - `def model_impact(before: Workflow, after: Workflow) -> dict` in `domain/impact`.
<!-- okf:generated:end links -->
