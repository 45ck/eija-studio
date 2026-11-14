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
  sha256: da87eecb78d2acd4ed26dde9e6c0fc32ee56ce6e4aed36002211deb14816b6d9
notes_baseline: 7205acb1bedcaddb3ad6c90c2d8cb42cbde04b10dae73e808eeb80b8ee803f43
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
