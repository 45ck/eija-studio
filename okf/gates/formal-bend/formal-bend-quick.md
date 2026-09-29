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
  sha256: f641765bd29da4dae06ad892d38dfb4ff1cb946718c345143a0bdfa67efb6627
notes_baseline: 7583c59839a0eff9ae9cebccb91eb817195dd57a751dd3dae150497e823ba9cf
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
