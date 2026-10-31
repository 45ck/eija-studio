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
  sha256: 392acd9f65b480cb32324900b473aac480e5d2c46c4a11aebdfa988cada3df70
notes_baseline: 92fc5a7bb743c69097adc77fa1212732731f7e76bfa5d825fc4b3104b3f19bd3
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
