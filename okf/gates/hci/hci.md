---
type: Quality Gate
title: nox -s hci
description: Drive real Chrome through the owner journey against a real `eija serve`; enforce the HCI budgets.
resource: repo://quality/sessions/hci.py#hci
tags:
- gate
- full
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/hci.py#hci
  title: hci.py
  hash_method: ast-v2
  sha256: 24da7f0bc8746f2a7afdecc97f7cc925492d7209de31bea8703ccec380b93680
notes_baseline: 3020a3d133e311d4965e49147e618ccd6d92dd5f312101cc656e1067f35e2fcb
---

# nox -s hci

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s hci` |
| Tiers | `full`, `release` |
| Session module | `repo://quality/sessions/hci.py` |
| Code | `repo://quality/sessions/hci.py#hci` |

## Docstring

~~~text
Drive real Chrome through the owner journey against a real `eija serve`; enforce the HCI budgets.

Writes reports/hci/{report.json,REPORT.md}. Chrome, Playwright or axe unavailable -> the session is
SKIPPED with a NOT_RUN reason (nox lists it as skipped): a missing prerequisite is never a pass.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
