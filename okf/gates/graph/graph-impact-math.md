---
type: Quality Gate
title: nox -s graph_impact_math
description: 'ADR-0097: hand-verified oracles for impact, ranking, selection, status algebra and confidence statistics (about 10 s).'
resource: repo://quality/sessions/graph.py#graph_impact_math
tags:
- gate
- fast
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/graph.py#graph_impact_math
  title: graph.py
  hash_method: ast-v2
  sha256: 99d0d07766a8feecd872a8db97fab943b32c9d9079d0ef8c6020ffd2d0e3c959
notes_baseline: c82cdf5b07f5be1fbb2d4a4552757b1c69f992ea61efd73ae962a697bcd5903b
---

# nox -s graph_impact_math

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s graph_impact_math` |
| Tiers | `fast`, `full` |
| Session module | `repo://quality/sessions/graph.py` |
| Code | `repo://quality/sessions/graph.py#graph_impact_math` |

## Docstring

~~~text
ADR-0097: hand-verified oracles for impact, ranking, selection, status algebra and confidence statistics (about 10 s).

Differential checks against graph/formal/eijaref, the kernel and networkx skip as NOT_RUN when that artefact is absent.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
