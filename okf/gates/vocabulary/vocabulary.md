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
  sha256: 28b686f113cdf91cefdc487b8f39f2e8d60d20c8c6928fca545aa7b8d838a107
notes_baseline: db43739fe0d05ace3255c716b87c18f0c57d4801a107c5d6210d5bbf9789ba7c
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
