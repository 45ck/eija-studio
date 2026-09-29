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
  sha256: f6cb40b5202c1d28af2c8c72779e3f91e49f7fa65ed86e36b56d7671fa607849
description_override: Fixed-point, cycle-safe reachability over a dependency graph; a budget yields complete=false and an explicit frontier, never a silent cap.
notes_baseline: 36c3602e003f288f9fffa19b2d2afbbcb42c5f0be80d4506642e7842c755a354
verified:
- by: process:claude-code-integration-phase0
  at: '2026-09-29T04:30:00Z'
  notes_sha256: 48f905dc561806a65a255bdf1d419cefc1cbf94f1cdd982de9ae6c02a7f818d9
  sources_sha256: 36c3602e003f288f9fffa19b2d2afbbcb42c5f0be80d4506642e7842c755a354
---

# domain.impact.closure

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/impact`](/modules/domain/impact.md) |
| Signature | `def closure(graph: dict[str, list[str]], roots: list[str], budget: int \| None=None) -> dict[str, Any]` |
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

* [domain.impact.model_impact](/symbols/domain/impact/model_impact.md) - `def model_impact(before: Workflow, after: Workflow) -> dict[str, Any]` in `domain/impact`.
<!-- okf:generated:end links -->
