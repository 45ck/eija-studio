---
type: Quality Gate
title: nox -s formal_smt
description: Z3 proof that check_policy admits only authority-preserving candidates (+ sampled faithfulness + negative controls).
resource: repo://quality/sessions/smt_bmc.py#formal_smt
tags:
- gate
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/smt_bmc.py#formal_smt
  title: smt_bmc.py
  hash_method: ast-v2
  sha256: a806f9d0ebee51acd379f6ffb397349ff92932fbc498c29b93d48a880b5e2863
notes_baseline: 2fa489e19dd0039f99dc2983bb4298faf0b7f1059f47745677c85616f6319a6c
---

# nox -s formal_smt

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s formal_smt` |
| Tiers | `full` |
| Session module | `repo://quality/sessions/smt_bmc.py` |
| Code | `repo://quality/sessions/smt_bmc.py#formal_smt` |

## Docstring

~~~text
Z3 proof that check_policy admits only authority-preserving candidates (+ sampled faithfulness + negative controls).
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
