---
type: Quality Gate
title: nox -s tests
description: Unit, integration, crash-recovery and concurrency tests of the kernel.
resource: repo://quality/sessions/tests.py#tests
tags:
- gate
- fast
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/tests.py#tests
  title: tests.py
  hash_method: ast-v2
  sha256: a14a0f95e793332ba6004a6c935af68ffaa78c581c6bd5a68d85f25d9052d547
notes_baseline: f24158097f135f4d9bdac9f334e4452e68e0e7f5f95ed1ede1c8cd95e15552b3
---

# nox -s tests

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s tests` |
| Tiers | `fast` |
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
