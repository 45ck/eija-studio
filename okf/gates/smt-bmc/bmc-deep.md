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
  sha256: 261f58c10d008c0825ac4781e8619f6961ccb965442c089d90fe655cc50cebb1
notes_baseline: 9a77f40ba40910642bdb80cc260ee346b3e3502f18c7020bbf9de1fad9f33a45
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
