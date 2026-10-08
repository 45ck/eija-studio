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
  sha256: 5f25844ca72dce68ca8cc08f1e7eff50adbed0787b525d6cd353be4e99c8e267
notes_baseline: b54d89044654308806af5d382cf12db7e3c1fdd5cbca452788c7f3a5f09aeef9
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
