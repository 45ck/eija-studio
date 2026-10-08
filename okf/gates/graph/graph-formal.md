---
type: Quality Gate
title: nox -s graph_formal
description: 'ADR-0102: stage-0 self-check of the trusted kernel references, then the fast formal tests (about 15 s).'
resource: repo://quality/sessions/graph.py#graph_formal
tags:
- gate
- fast
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/graph.py#graph_formal
  title: graph.py
  hash_method: ast-v2
  sha256: d7fd42bb6035c6ca1abc2461b7fbc5070d2a300ec51326847553aeeacac0b643
notes_baseline: 46a8c301abec6fa8a6abaf07bcec0aa825ea837b687a75ae10cb7fd2e87a3459
---

# nox -s graph_formal

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s graph_formal` |
| Tiers | `fast` |
| Session module | `repo://quality/sessions/graph.py` |
| Code | `repo://quality/sessions/graph.py#graph_formal` |

## Docstring

~~~text
ADR-0102: stage-0 self-check of the trusted kernel references, then the fast formal tests (about 15 s).

Missing Hypothesis, clingo, rfc8785, Java or the pinned Alloy jar make the affected tests skip: the output names NOT_RUN, never a pass.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
