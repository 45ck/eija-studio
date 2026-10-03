---
type: Quality Gate
title: nox -s metrics
description: Collect metrics (quick profile), gate structural budgets, verify the dashboard is not stale.
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
  sha256: faa37067e19294004376baa09704a14c88915a7487aa469a2dec0db03d239570
notes_baseline: b31e9142f965e769a607a125b5f9d32210a5410276dd9193847e500b1c66bd1f
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
Collect metrics (quick profile), gate structural budgets, verify the dashboard is not stale.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
