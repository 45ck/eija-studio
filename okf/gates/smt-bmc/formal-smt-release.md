---
type: Quality Gate
title: nox -s formal_smt_release
description: 'Release tier: the same proof with a 4x larger differential sample; a missing z3-solver fails instead of skipping.'
resource: repo://quality/sessions/smt_bmc.py#formal_smt_release
tags:
- gate
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/smt_bmc.py#formal_smt_release
  title: smt_bmc.py
  hash_method: ast-v2
  sha256: 80afdbcd09af6f99d03e056026103dca6b22cd65edbd39c3a7d3ddfcdc645032
notes_baseline: 4f892dc53aae0441afd20a6270de38f9a9eb1dbf6cd767425fcc1145a0f8ec43
---

# nox -s formal_smt_release

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s formal_smt_release` |
| Tiers | `release` |
| Session module | `repo://quality/sessions/smt_bmc.py` |
| Code | `repo://quality/sessions/smt_bmc.py#formal_smt_release` |

## Docstring

~~~text
Release tier: the same proof with a 4x larger differential sample; a missing z3-solver fails instead of skipping.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
