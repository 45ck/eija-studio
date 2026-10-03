---
type: Quality Gate
title: nox -s docs
description: Build the MkDocs Material site with --strict.
resource: repo://quality/sessions/oss.py#docs
tags:
- gate
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/oss.py#docs
  title: oss.py
  hash_method: ast-v2
  sha256: 7b9ed6b1778c07a3eed99f3ebdeeda836d59d42095f327f6d26c214cffb1298b
notes_baseline: 75a65eceafa099cf16e292e6b2b4b618a4cfd7a10dfc2615da6bed789b1502a3
---

# nox -s docs

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s docs` |
| Tiers | `release` |
| Session module | `repo://quality/sessions/oss.py` |
| Code | `repo://quality/sessions/oss.py#docs` |

## Docstring

~~~text
Build the MkDocs Material site with --strict. NOT_RUN when MkDocs (extra `docs`) is not installed.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
