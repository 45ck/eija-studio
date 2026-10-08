---
type: Quality Gate
title: nox -s lint
description: Ruff lint (bugbear, bandit subset, simplify, pyupgrade, pylint subset); format check of lane files.
resource: repo://quality/sessions/quality.py#lint
tags:
- gate
- fast
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/quality.py#lint
  title: quality.py
  hash_method: ast-v2
  sha256: 6ecdce715a708e77893216bc6398084f5830b7ebd397683322d56bb5e9f4b9cb
notes_baseline: 830d48324ee4d9a4d540f66634099ea57b90a6d7167fe7a308f3552d9eeb26bb
---

# nox -s lint

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s lint` |
| Tiers | `fast`, `full` |
| Session module | `repo://quality/sessions/quality.py` |
| Code | `repo://quality/sessions/quality.py#lint` |

## Docstring

~~~text
Ruff lint (bugbear, bandit subset, simplify, pyupgrade, pylint subset); format check of lane files.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
