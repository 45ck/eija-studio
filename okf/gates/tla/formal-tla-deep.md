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
  sha256: 10d512b17b6294c8921449448a5433fe0f7c4c0308d7d58ac7dbcce1b2e590fe
notes_baseline: 64e414179a0fc6c086fe9dbf0e87c9cd3b301f9f766d31a77e537989cfe30f13
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
