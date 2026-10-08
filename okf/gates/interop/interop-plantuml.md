---
type: Quality Gate
title: nox -s interop_plantuml
description: PlantUML reads every PlantUML export as PlayIDE does; its negative controls are caught.
resource: repo://quality/sessions/interop.py#interop_plantuml
tags:
- gate
- full
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/interop.py#interop_plantuml
  title: interop.py
  hash_method: ast-v2
  sha256: 56c3d3e0e966dd33edbdfef0d8d17f43997ba7270daeeefca896b5e4255a2325
notes_baseline: 5471155090ca5b626dea6a5b03705019f580cc909f1e3b1ee16d4ecb475b2076
---

# nox -s interop_plantuml

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s interop_plantuml` |
| Tiers | `full`, `release` |
| Session module | `repo://quality/sessions/interop.py` |
| Code | `repo://quality/sessions/interop.py#interop_plantuml` |

## Docstring

~~~text
PlantUML reads every PlantUML export as PlayIDE does; its negative controls are caught.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
