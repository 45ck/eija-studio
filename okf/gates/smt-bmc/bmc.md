---
type: Quality Gate
title: nox -s bmc
description: Bounded model check of the real runtime to depth 6 (baseline + recommendation candidate), with seeded-fault self-test.
resource: repo://quality/sessions/smt_bmc.py#bmc
tags:
- gate
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/smt_bmc.py#bmc
  title: smt_bmc.py
  hash_method: ast-v2
  sha256: 0ba8f9324dbe1f82d545a155429997f0c0288eb208c97f0f85edf73096fbaf9a
notes_baseline: e33dd1fabd3a18687e01f29709bdb80cb2964e71c8fba9e22eb87cbcc9d7ba01
---

# nox -s bmc

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s bmc` |
| Tiers | `full` |
| Session module | `repo://quality/sessions/smt_bmc.py` |
| Code | `repo://quality/sessions/smt_bmc.py#bmc` |

## Docstring

~~~text
Bounded model check of the real runtime to depth 6 (baseline + recommendation candidate), with seeded-fault self-test.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
