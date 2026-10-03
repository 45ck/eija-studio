---
type: Quality Gate
title: nox -s okf_structure
description: OKF v0.2 conformance and internal links of the committed wiki (no source hashing, no regeneration).
resource: repo://quality/sessions/okf.py#okf_structure
tags:
- gate
- fast
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/okf.py#okf_structure
  title: okf.py
  hash_method: ast-v2
  sha256: 927eebcfc00d3c8ed42046a409cb7d1aa2affe2251acda0ce908145256fbee61
notes_baseline: c962ae694235d6309ed8ee18587ef02329432bd6d184411269b2c99f272dc4f1
---

# nox -s okf_structure

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s okf_structure` |
| Tiers | `fast` |
| Session module | `repo://quality/sessions/okf.py` |
| Code | `repo://quality/sessions/okf.py#okf_structure` |

## Docstring

~~~text
OKF v0.2 conformance and internal links of the committed wiki (no source hashing, no regeneration).

Fast on purpose and independent of other lanes' code edits, so it stays green while they change the kernel.
The code-linked checks (STALE, coverage, drift) live in `okf`, the integration gate. A PASS establishes that
the wiki is well-formed and its links resolve; nothing about whether it matches the code.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
