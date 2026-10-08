---
type: Quality Gate
title: nox -s mutation
description: Full mutation run over the domain and application authority/evidence modules, gated by the ratchet floor.
resource: repo://quality/sessions/mutation.py#mutation
tags:
- gate
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/mutation.py#mutation
  title: mutation.py
  hash_method: ast-v2
  sha256: f5cb10c959966bd53c83af6fae205ce3b29b9d93f79fc2290a533a079d48c071
notes_baseline: 3f24a6bc495790ef87cca168e20c8d2d29a074928da664423e7797c09a5939a6
---

# nox -s mutation

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s mutation` |
| Tiers | `release` |
| Session module | `repo://quality/sessions/mutation.py` |
| Code | `repo://quality/sessions/mutation.py#mutation` |

## Docstring

~~~text
Full mutation run over the domain and application authority/evidence modules, gated by the ratchet floor.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
