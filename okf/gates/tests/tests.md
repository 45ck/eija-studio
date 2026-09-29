---
type: Quality Gate
title: nox -s tests
description: Unit, integration, crash-recovery and concurrency tests of the kernel.
resource: repo://quality/sessions/tests.py#tests
tags:
- gate
- fast
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/tests.py#tests
  title: tests.py
  hash_method: ast-v2
  sha256: 5ac6913613ca601b1b42a033f77ac29c0b9df8e1673109a1f5566e3c857e12f1
notes_baseline: 3f47412480429c78ef78d286bb021fd31d5d9985d7f519c36759f93abbb14342
---

# nox -s tests

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s tests` |
| Tiers | `fast`, `full` |
| Session module | `repo://quality/sessions/tests.py` |
| Code | `repo://quality/sessions/tests.py#tests` |

## Docstring

~~~text
Unit, integration, crash-recovery and concurrency tests of the kernel.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
