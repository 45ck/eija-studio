---
type: Quality Gate
title: nox -s demos_typecheck
description: mypy over the demos package (the shared mypy config names only eija_studio).
resource: repo://quality/sessions/demos.py#demos_typecheck
tags:
- gate
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/demos.py#demos_typecheck
  title: demos.py
  hash_method: ast-v2
  sha256: e8bd81c75f02a4581ac9af77b23e9c1b74758abef5958825910d1cb9822ffbd9
notes_baseline: 8c777397854136c9ac6e7a5c28d154714c1ae9911661b81ab4110819327f591d
---

# nox -s demos_typecheck

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s demos_typecheck` |
| Tiers | `full` |
| Session module | `repo://quality/sessions/demos.py` |
| Code | `repo://quality/sessions/demos.py#demos_typecheck` |

## Docstring

~~~text
mypy over the demos package (the shared mypy config names only eija_studio).
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
