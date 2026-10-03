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
  sha256: de65f8933b08e718de1d6d3759e9be467176ed797975eb1d54cd080378fef73f
notes_baseline: 0a884b970e80fa5e4e4c33caa1f5dce4c5daf8732d26ebe55746b327d260ec26
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
