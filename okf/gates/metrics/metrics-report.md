---
type: Quality Gate
title: nox -s metrics_report
description: 'Release evidence: coverage export, full-profile measurement (median and IQR), all budgets, dashboard in reports/metrics/.'
resource: repo://quality/sessions/metrics.py#metrics_report
tags:
- gate
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/metrics.py#metrics_report
  title: metrics.py
  hash_method: ast-v2
  sha256: 4f3d1996a5e6f1ffa6ed13b5934397ca4d544d173eb54c2255970670311663e4
notes_baseline: 7287c8e200feafea5a17e65dd9bfefccb00e18abfac75bfdfd5be9be466c0b19
---

# nox -s metrics_report

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s metrics_report` |
| Tiers | `release` |
| Session module | `repo://quality/sessions/metrics.py` |
| Code | `repo://quality/sessions/metrics.py#metrics_report` |

## Docstring

~~~text
Release evidence: coverage export, full-profile measurement (median and IQR), all budgets, dashboard in reports/metrics/.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
