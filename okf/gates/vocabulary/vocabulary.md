---
type: Quality Gate
title: nox -s vocabulary
description: Pack tokens outside packs/, GENERATED files and the justified allowlist fail; so does any Literal naming one.
resource: repo://quality/sessions/vocabulary.py#vocabulary
tags:
- gate
- fast
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/vocabulary.py#vocabulary
  title: vocabulary.py
  hash_method: ast-v2
  sha256: f1db61e66c1096f934538440254da2aeceff06c582233bdf1ad0f0a869698f3b
notes_baseline: f3be75c9771837af139a56986bdf9bd269e2f1681972e0074de7048606b9c9cb
---

# nox -s vocabulary

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s vocabulary` |
| Tiers | `fast`, `full` |
| Session module | `repo://quality/sessions/vocabulary.py` |
| Code | `repo://quality/sessions/vocabulary.py#vocabulary` |

## Docstring

~~~text
Pack tokens outside packs/, GENERATED files and the justified allowlist fail; so does any Literal naming one.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
