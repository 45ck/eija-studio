---
type: Quality Gate
title: nox -s dependencies
description: 'deptry: every import is declared, every declared runtime dependency is used.'
resource: repo://quality/sessions/quality.py#dependencies
tags:
- gate
- fast
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/quality.py#dependencies
  title: quality.py
  hash_method: ast-v2
  sha256: 28e3929ed454d7c77b8239bbbf4681684b9caa90c6e18e4ced01c88f5bcb9a83
notes_baseline: 9fcb155be13036d187ec3cb390d3f3d96ed9613d16eb28a9520188e61ef12f2c
---

# nox -s dependencies

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s dependencies` |
| Tiers | `fast`, `full` |
| Session module | `repo://quality/sessions/quality.py` |
| Code | `repo://quality/sessions/quality.py#dependencies` |

## Docstring

~~~text
deptry: every import is declared, every declared runtime dependency is used.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
