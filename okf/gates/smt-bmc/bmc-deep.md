---
type: Quality Gate
title: nox -s bmc_deep
description: 'Release-tier bounded model check: depth 8 over all three workflow variants (several minutes).'
resource: repo://quality/sessions/smt_bmc.py#bmc_deep
tags:
- gate
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/smt_bmc.py#bmc_deep
  title: smt_bmc.py
  hash_method: ast-v2
  sha256: 3267c33d3cc89c0e0d25e42a5ac1ae7eee5624b16b772d7df985f705ab835c8e
notes_baseline: 0ecb597c506ee3b4582a530bdcb1679985a7142ee091ebb860da4789eb3b0edb
---

# nox -s bmc_deep

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s bmc_deep` |
| Tiers | `release` |
| Session module | `repo://quality/sessions/smt_bmc.py` |
| Code | `repo://quality/sessions/smt_bmc.py#bmc_deep` |

## Docstring

~~~text
Release-tier bounded model check: depth 8 over all three workflow variants (several minutes).
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
