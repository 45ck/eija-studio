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
  hash_method: ast-v1
  sha256: b28512648832d2d4749e7d6fbed5cabdbfc564e1beb4bad9149e85ec78fb61b3
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
