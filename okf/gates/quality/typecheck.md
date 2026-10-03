---
type: Quality Gate
title: nox -s typecheck
description: 'mypy: strict on eija_studio.domain and .application, default profile with a ratchet plan elsewhere.'
resource: repo://quality/sessions/quality.py#typecheck
tags:
- gate
- fast
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/quality.py#typecheck
  title: quality.py
  hash_method: ast-v2
  sha256: 64e327f6a277b991b553a2134874131c6c8fb60b51ef12a2c28097d1bd65a2c8
notes_baseline: 1af1026ad3efc8007808f3ad094c689d843c738096905bb467707a2e0ac6ba41
---

# nox -s typecheck

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s typecheck` |
| Tiers | `fast`, `full` |
| Session module | `repo://quality/sessions/quality.py` |
| Code | `repo://quality/sessions/quality.py#typecheck` |

## Docstring

~~~text
mypy: strict on eija_studio.domain and .application, default profile with a ratchet plan elsewhere.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
