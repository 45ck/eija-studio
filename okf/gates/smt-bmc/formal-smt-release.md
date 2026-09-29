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
  sha256: 74df43049aea14cab6374937807ba585073918d4947b98bd8d1a81582df3a7ed
notes_baseline: 1653a019225d1f112f6ae19a14bb263d7f5b0f0e478c77793e7bd5c9a269620c
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
