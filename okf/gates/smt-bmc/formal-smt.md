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
  sha256: 06d33d9ad6ef318aae098d9dfe23ef511491c2ff0fbb70679497b58c9e7333be
notes_baseline: 06c5406a794bca0297cd953be1287b414a6c44ce1acd3127d796ab09080c2dd2
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
