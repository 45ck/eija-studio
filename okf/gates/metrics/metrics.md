---
type: Quality Gate
title: nox -s metrics
description: Structural metrics (Martin, complexity, test inventory), structural budgets, dashboard renders from its snapshot.
resource: repo://quality/sessions/metrics.py#metrics
tags:
- gate
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/metrics.py#metrics
  title: metrics.py
  hash_method: ast-v2
  sha256: d87bd7dce45b2bde5d10e1d87f10009842d6aea8e59952b6e62acd82df85e0b7
notes_baseline: fccb354082c070e16554490cd7798447ff2af244b667f9ce54675aa1c1dbe0ce
---

# nox -s metrics

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s metrics` |
| Tiers | `full` |
| Session module | `repo://quality/sessions/metrics.py` |
| Code | `repo://quality/sessions/metrics.py#metrics` |

## Docstring

~~~text
Structural metrics (Martin, complexity, test inventory), structural budgets, dashboard renders from its snapshot.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
