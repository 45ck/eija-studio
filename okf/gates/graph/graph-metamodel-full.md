---
type: Quality Gate
title: nox -s graph_metamodel_full
description: 'ADR-0089: every metamodel and identity oracle, including byte identity of the bench report across PYTHONHASHSEED values.'
resource: repo://quality/sessions/graph.py#graph_metamodel_full
tags:
- gate
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/graph.py#graph_metamodel_full
  title: graph.py
  hash_method: ast-v2
  sha256: 4eeae1650861ee10d55d55932300503ec3fe3712a2f0dacb840a6a75fb703bc3
notes_baseline: 6964448d1bd8c46e3c11d5dd49ee3bc50d701ca9ae03e2a28503cde6d372bae3
---

# nox -s graph_metamodel_full

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s graph_metamodel_full` |
| Tiers | `full` |
| Session module | `repo://quality/sessions/graph.py` |
| Code | `repo://quality/sessions/graph.py#graph_metamodel_full` |

## Docstring

~~~text
ADR-0089: every metamodel and identity oracle, including byte identity of the bench report across PYTHONHASHSEED values.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
