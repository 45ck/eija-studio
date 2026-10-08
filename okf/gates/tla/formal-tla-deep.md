---
type: Quality Gate
title: nox -s formal_tla_deep
description: formal_tla plus the candidate model checked with 5 operation ids (about 28k states).
resource: repo://quality/sessions/tla.py#formal_tla_deep
tags:
- gate
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/tla.py#formal_tla_deep
  title: tla.py
  hash_method: ast-v2
  sha256: 57e6b0adb5dd8b9f41fea0df66b7ed719c2a5cd324700b652ba7ca9ad4cab383
notes_baseline: 06e07846513c91d46a0539f56f10c05f532b0bee8f4947f54feff730b74a2b56
---

# nox -s formal_tla_deep

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s formal_tla_deep` |
| Tiers | `release` |
| Session module | `repo://quality/sessions/tla.py` |
| Code | `repo://quality/sessions/tla.py#formal_tla_deep` |

## Docstring

~~~text
formal_tla plus the candidate model checked with 5 operation ids (about 28k states).
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
