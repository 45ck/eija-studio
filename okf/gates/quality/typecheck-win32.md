---
type: Quality Gate
title: nox -s typecheck_win32
description: 'mypy again as win32: Windows-only branches (subprocess creation flags, msvcrt) are invisible to the linux run.'
resource: repo://quality/sessions/quality.py#typecheck_win32
tags:
- gate
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/quality.py#typecheck_win32
  title: quality.py
  hash_method: ast-v2
  sha256: be997653e952823d16f1cb891b856b1e0f53ba4983ec362300a0da5153bc7cf8
notes_baseline: cacbacb72438063c99f2945b868dc49f0fdeb5c00bcc3d083a6732b139a6423c
---

# nox -s typecheck_win32

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s typecheck_win32` |
| Tiers | `full` |
| Session module | `repo://quality/sessions/quality.py` |
| Code | `repo://quality/sessions/quality.py#typecheck_win32` |

## Docstring

~~~text
mypy again as win32: Windows-only branches (subprocess creation flags, msvcrt) are invisible to the linux run.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
