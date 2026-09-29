---
type: Quality Gate
title: nox -s diagrams_drift
description: docs/diagrams/*.md equal a fresh render of the executable model (no browser, no network).
resource: repo://quality/sessions/visual.py#diagrams_drift
tags:
- gate
- fast
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/visual.py#diagrams_drift
  title: visual.py
  hash_method: ast-v2
  sha256: 0f7fe513a0cdfdef57034b069bf1729d371d2543dfa85a32fb1970adc9791698
notes_baseline: 3dc9a224382a51544a7e0dad2c09e0cc2ff184175c306d7347a79117edcdb662
---

# nox -s diagrams_drift

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s diagrams_drift` |
| Tiers | `fast`, `full` |
| Session module | `repo://quality/sessions/visual.py` |
| Code | `repo://quality/sessions/visual.py#diagrams_drift` |

## Docstring

~~~text
docs/diagrams/*.md equal a fresh render of the executable model (no browser, no network).
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
