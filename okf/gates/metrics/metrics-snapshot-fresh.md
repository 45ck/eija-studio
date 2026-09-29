---
type: Quality Gate
title: nox -s metrics_snapshot_fresh
description: 'Release tier: the committed snapshot''s deterministic sections describe the CURRENT source (strict drift check).'
resource: repo://quality/sessions/metrics.py#metrics_snapshot_fresh
tags:
- gate
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/metrics.py#metrics_snapshot_fresh
  title: metrics.py
  hash_method: ast-v2
  sha256: 407b04cee08335e4c8f85c0cd6ecd15c94a03f21a6b303fb47c4007ff7b43a02
notes_baseline: 1f77aa448094ad67a34ff9963881e86b01648e82540c536b3526bdfcea8b31ce
---

# nox -s metrics_snapshot_fresh

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s metrics_snapshot_fresh` |
| Tiers | `release` |
| Session module | `repo://quality/sessions/metrics.py` |
| Code | `repo://quality/sessions/metrics.py#metrics_snapshot_fresh` |

## Docstring

~~~text
Release tier: the committed snapshot's deterministic sections describe the CURRENT source (strict drift check).
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
