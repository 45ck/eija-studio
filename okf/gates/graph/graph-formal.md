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
  sha256: 47a20094a438ae910866f34c783f341e7d9a7dcfe557b3a9a751143326eed5bd
notes_baseline: aa4d1652ffdaad1c50ac5a962e10e1861d05fde8cf3674b5d63fd5acb013d1da
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
