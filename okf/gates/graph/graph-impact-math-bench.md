---
type: Quality Gate
title: nox -s graph_impact_math_bench
description: 'ADR-0097 MEASUREMENTS: cost of the reference implementations.'
resource: repo://quality/sessions/graph.py#graph_impact_math_bench
tags:
- gate
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/graph.py#graph_impact_math_bench
  title: graph.py
  hash_method: ast-v2
  sha256: eeb4ada4679711786d685ae8c382e35dad5a675741dfa526e0768099b895e622
notes_baseline: 026e645e3cb7db55095f32cf1d1a1b3ac6ecfca614ed59ca7edb448858d0926e
---

# nox -s graph_impact_math_bench

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s graph_impact_math_bench` |
| Tiers | `release` |
| Session module | `repo://quality/sessions/graph.py` |
| Code | `repo://quality/sessions/graph.py#graph_impact_math_bench` |

## Docstring

~~~text
ADR-0097 MEASUREMENTS: cost of the reference implementations. The co-change ranking study needs external clones and is run
by hand (docs/weave/design/impact-ranking-and-confidence.md section 16); it is NOT_RUN here, never a pass.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
