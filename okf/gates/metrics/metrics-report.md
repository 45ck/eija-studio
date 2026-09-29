---
type: Quality Gate
title: nox -s metrics_report
description: 'Release evidence: coverage run, full-profile measurement, all budgets, fresh snapshot, dashboard in reports/metrics/.'
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
  sha256: ed901da7b3bd4b628b9de4c32fd83d453d29135be9bd37fc8a2a2ef0e7dc9afa
notes_baseline: d93ed3d3a7f792ca0d326710ae2d9edeb841562f8ed65373bb2e6dbfc1d6dcf4
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
Release evidence: coverage run, full-profile measurement, all budgets, fresh snapshot, dashboard in reports/metrics/.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
