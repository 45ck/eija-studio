---
type: Quality Gate
title: nox -s appgen
description: '`eija build` for each pack into reports/appgen/; a FAIL (exit 2) or refusal fails the session.'
resource: repo://quality/sessions/appgen.py#appgen
tags:
- gate
- full
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/appgen.py#appgen
  title: appgen.py
  hash_method: ast-v2
  sha256: 90a26c94a330b0c75deb01ed9e00e6a4c33bf950989f05a082d49bc19b17bf4d
notes_baseline: 3da5e836fbb1c87213bdefb5f1529dde1db6833395f94212201fe663b0e93d50
---

# nox -s appgen

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s appgen` |
| Tiers | `full`, `release` |
| Session module | `repo://quality/sessions/appgen.py` |
| Code | `repo://quality/sessions/appgen.py#appgen` |

## Docstring

~~~text
`eija build` for each pack into reports/appgen/; a FAIL (exit 2) or refusal fails the session.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
