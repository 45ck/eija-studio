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
  sha256: 514a391264d9d7797e27f8a4503c6ed2869f6e51faefe53f85f05a87bd47953a
notes_baseline: 40b933fd115de38f66d2c8b1931755888da1f66c18b2b1d7a3573f0316a80917
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
