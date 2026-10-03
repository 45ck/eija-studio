---
type: Quality Gate
title: nox -s complexity
description: xenon module/average rank ceilings plus the per-function ratchet.
resource: repo://quality/sessions/quality.py#complexity
tags:
- gate
- fast
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/quality.py#complexity
  title: quality.py
  hash_method: ast-v2
  sha256: 57ed0f9223cdf1b1d677b98da6ac28d053afa338cf9b168d4da86cc032d8244f
notes_baseline: c943677bb924b0dd600a9810194054ef6a09946bd307664bec9011da5e6e536d
---

# nox -s complexity

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s complexity` |
| Tiers | `fast`, `full` |
| Session module | `repo://quality/sessions/quality.py` |
| Code | `repo://quality/sessions/quality.py#complexity` |

## Docstring

~~~text
xenon module/average rank ceilings plus the per-function ratchet.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
