---
type: Quality Gate
title: nox -s release_fixture
description: 'Owner-only release gate: current bytes must match the owner-stamped fixture.'
resource: repo://quality/sessions/tests.py#release_fixture
tags:
- gate
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/tests.py#release_fixture
  title: tests.py
  hash_method: ast-v1
  sha256: 2ab8a312a1c471d83072f2da018fd0d5322f6c33c3a9ad43113067dca88fbbe8
---

# nox -s release_fixture

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s release_fixture` |
| Tiers | `release` |
| Session module | `repo://quality/sessions/tests.py` |
| Code | `repo://quality/sessions/tests.py#release_fixture` |

## Docstring

~~~text
Owner-only release gate: current bytes must match the owner-stamped fixture. Agents never stamp.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
