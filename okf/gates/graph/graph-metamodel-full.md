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
  sha256: 7ce3d9e73c669378d828a3ce9c9375f41460857a5f499421b785ba66240fc6e4
notes_baseline: 0decc56a00ceaddc70792023c346f2143c0312d1bc741f20332b5209e162e96e
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
