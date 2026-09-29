---
type: Quality Gate
title: nox -s bend_drift
description: The committed Bend model equals regeneration from the executable Workflow; laws and proofs pair up.
resource: repo://quality/sessions/formal_bend.py#bend_drift
tags:
- gate
- fast
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/formal_bend.py#bend_drift
  title: formal_bend.py
  hash_method: ast-v2
  sha256: c08a4d517536b00eb33faabd6a36c8e411a754fafb497811464019d42ad2251c
notes_baseline: 1c204f98a13670e7993957e141f7eda1119675140ac94c1e06bbb7e7d7a961c6
---

# nox -s bend_drift

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s bend_drift` |
| Tiers | `fast`, `full` |
| Session module | `repo://quality/sessions/formal_bend.py` |
| Code | `repo://quality/sessions/formal_bend.py#bend_drift` |

## Docstring

~~~text
The committed Bend model equals regeneration from the executable Workflow; laws and proofs pair up.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
