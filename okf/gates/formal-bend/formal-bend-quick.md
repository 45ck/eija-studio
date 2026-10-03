---
type: Quality Gate
title: nox -s formal_bend_quick
description: bend PROOF.bend --verdict in the pinned container, negative controls, runtime conformance.
resource: repo://quality/sessions/formal_bend.py#formal_bend_quick
tags:
- gate
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/formal_bend.py#formal_bend_quick
  title: formal_bend.py
  hash_method: ast-v2
  sha256: 66778d3e479f1495c84f38ceb58d517185984e15ac4a412eae511d319c8b9765
notes_baseline: 697f588ef7e89579c7f1bc252e90cedc04b1f010016e1ef6b30f03e735d17bce
---

# nox -s formal_bend_quick

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s formal_bend_quick` |
| Tiers | `full` |
| Session module | `repo://quality/sessions/formal_bend.py` |
| Code | `repo://quality/sessions/formal_bend.py#formal_bend_quick` |

## Docstring

~~~text
bend PROOF.bend --verdict in the pinned container, negative controls, runtime conformance.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
