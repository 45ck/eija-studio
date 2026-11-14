---
type: Quality Gate
title: nox -s graph_formal_release
description: 'ADR-0102 MEASUREMENTS and solver diversity: all formal benchmarks, then the Alloy certificate models on a second SAT backend (SAT4J, about 4 minutes).'
resource: repo://quality/sessions/graph.py#graph_formal_release
tags:
- gate
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/graph.py#graph_formal_release
  title: graph.py
  hash_method: ast-v2
  sha256: 0ba13d8d235c43d59035f8e6d99df99f07cffc8e9959d3af9f635ee54a1a4362
notes_baseline: d647344ee92eafe4f68f9e9cca16bff4df88d80ec5de1a8a2ee83315e63fbf46
---

# nox -s graph_formal_release

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s graph_formal_release` |
| Tiers | `release` |
| Session module | `repo://quality/sessions/graph.py` |
| Code | `repo://quality/sessions/graph.py#graph_formal_release` |

## Docstring

~~~text
ADR-0102 MEASUREMENTS and solver diversity: all formal benchmarks, then the Alloy certificate models on a second SAT backend (SAT4J, about 4 minutes).

A disagreement between the two backends is a FAIL. POSIX byte identity of the report is NOT_RUN until run on Linux or WSL.
Run serially: one JVM at a time on the shared PC.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
