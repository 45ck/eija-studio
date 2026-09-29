---
type: Quality Gate
title: nox -s graph_formal_full
description: 'ADR-0102: every formal test, the exhaustive enumerations (about 1 minute) and the Alloy certificate models (Glucose, about 25 s).'
resource: repo://quality/sessions/graph.py#graph_formal_full
tags:
- gate
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/graph.py#graph_formal_full
  title: graph.py
  hash_method: ast-v2
  sha256: 289d27ccb356b6b535ecf90c7e2b19e19ba16ffc4de2be12d4244b3203e29e2a
notes_baseline: c35235648ba96616e21dca7cab3387af423d4446b696268abd180a76a1b65186
---

# nox -s graph_formal_full

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s graph_formal_full` |
| Tiers | `full` |
| Session module | `repo://quality/sessions/graph.py` |
| Code | `repo://quality/sessions/graph.py#graph_formal_full` |

## Docstring

~~~text
ADR-0102: every formal test, the exhaustive enumerations (about 1 minute) and the Alloy certificate models (Glucose, about 25 s).

Java 17 and the jar pinned in graph/formal/TOOLS.lock are needed for the Alloy commands; without them they are NOT_RUN.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
