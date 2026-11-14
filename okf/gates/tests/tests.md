---
type: Quality Gate
title: nox -s tests
description: Unit, integration, crash-recovery and concurrency tests of the kernel; then the skip ledger.
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
  sha256: 4bc1d749f62d9f1005fd2f2284034c74781cde2df4036f9d0008cf69b785dde3
notes_baseline: 1956a206db37197bdc99a339cc878ef8362753a0e779426a760c54bd2b94f85e
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
Unit, integration, crash-recovery and concurrency tests of the kernel; then the skip ledger.

A skipped test inside a green session is NOT_RUN that nox cannot see, so the run writes junit and
quality/tools/skip_ledger.py fails on any skip the ledger does not record (a missing extra, a new importorskip).
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
