---
type: Quality Gate
title: nox -s tla_drift
description: The committed TLA+ model modules match the kernel's workflow, actor directory and bounds.
resource: repo://quality/sessions/tla.py#tla_drift
tags:
- gate
- fast
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/tla.py#tla_drift
  title: tla.py
  hash_method: ast-v2
  sha256: bd9cc802aeda718ed890c4dc43ee9dd1a687da7e9839484a10072f177a180948
notes_baseline: 5b12a6f28409bc61fc5ecc5fa6360a106abe7f0c80a5a77e6af350979ea55282
---

# nox -s tla_drift

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s tla_drift` |
| Tiers | `fast`, `full` |
| Session module | `repo://quality/sessions/tla.py` |
| Code | `repo://quality/sessions/tla.py#tla_drift` |

## Docstring

~~~text
The committed TLA+ model modules match the kernel's workflow, actor directory and bounds.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
