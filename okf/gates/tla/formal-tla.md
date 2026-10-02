---
type: Quality Gate
title: nox -s formal_tla
description: TLC model check of Excursion.tla, negative controls, and runtime-vs-spec conformance.
resource: repo://quality/sessions/tla.py#formal_tla
tags:
- gate
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/tla.py#formal_tla
  title: tla.py
  hash_method: ast-v2
  sha256: bb4344f1f394255ca6dc451bac82c55873e06a194e462e3177a3e1261c46f53f
notes_baseline: 5df55227a655cf53edaa35c8f9ca7537efd36e11870209ad174401fe0aeba36c
---

# nox -s formal_tla

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s formal_tla` |
| Tiers | `full` |
| Session module | `repo://quality/sessions/tla.py` |
| Code | `repo://quality/sessions/tla.py#formal_tla` |

## Docstring

~~~text
TLC model check of Excursion.tla, negative controls, and runtime-vs-spec conformance.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
