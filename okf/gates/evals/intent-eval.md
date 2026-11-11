---
type: Quality Gate
title: nox -s intent_eval
description: Grades the offline proposer on packs/intent-evals.json and checks the kernel agrees on every planned meaning.
resource: repo://quality/sessions/evals.py#intent_eval
tags:
- gate
- fast
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/evals.py#intent_eval
  title: evals.py
  hash_method: ast-v2
  sha256: 1d3eb4f4f74d1d89f52a79169a350e8c7acbe59ecb50b27465c16dcda24c184d
notes_baseline: c02dbf1e64d314667fc2d949c46fff3eef51c0e412765e58c8e7ebb8f9911727
---

# nox -s intent_eval

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s intent_eval` |
| Tiers | `fast`, `full` |
| Session module | `repo://quality/sessions/evals.py` |
| Code | `repo://quality/sessions/evals.py#intent_eval` |

## Docstring

~~~text
Grades the offline proposer on packs/intent-evals.json and checks the kernel agrees on every planned meaning.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
