---
type: Quality Gate
title: nox -s diagrams_syntax
description: Every emitted diagram is accepted by the real renderers, and the real-browser negative controls pass.
resource: repo://quality/sessions/visual.py#diagrams_syntax
tags:
- gate
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/visual.py#diagrams_syntax
  title: visual.py
  hash_method: ast-v2
  sha256: ba15d55021233cb7a4cf2778095a62c844e8756f1efe8be9d4c6f95365271383
notes_baseline: 007e99540c27c758528224b0920930dec418d9739b875d14ac89d2c000a08bd3
---

# nox -s diagrams_syntax

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s diagrams_syntax` |
| Tiers | `release` |
| Session module | `repo://quality/sessions/visual.py` |
| Code | `repo://quality/sessions/visual.py#diagrams_syntax` |

## Docstring

~~~text
Every emitted diagram is accepted by the real renderers, and the real-browser negative controls pass.
A renderer that could not run (Chrome, Playwright, Java, the PlantUML jar via EIJA_PLANTUML_JAR) is NOT_RUN and
FAILS this session (exit 3) unless EIJA_ALLOW_NOT_RUN=1 is set; the JSON on stdout still says NOT_RUN.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
