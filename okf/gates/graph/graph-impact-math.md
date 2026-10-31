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
  sha256: 78d5c9f73e13e259a7fb3e681528fec20fc099178ad179907c8641cc6ee7f26d
notes_baseline: c2935f5cd46c6f0a3f2611bc2e4e65ff65f01410dc66988c0b8f8f2fd09b3200
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
