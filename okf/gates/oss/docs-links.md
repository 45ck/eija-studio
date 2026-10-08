---
type: Quality Gate
title: nox -s docs_links
description: Relative links and heading anchors in README, community files and docs/ resolve (offline).
resource: repo://quality/sessions/oss.py#docs_links
tags:
- gate
- fast
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/oss.py#docs_links
  title: oss.py
  hash_method: ast-v2
  sha256: 5a90ccc5e91b9080c3c3126671b0d9a6353190eb227ea6088ab2affcfb3bd38c
notes_baseline: f1578544e6472fc02be61a6d97646620a27a12f7606dce631ba2d887e37d1d7e
---

# nox -s docs_links

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s docs_links` |
| Tiers | `fast`, `full` |
| Session module | `repo://quality/sessions/oss.py` |
| Code | `repo://quality/sessions/oss.py#docs_links` |

## Docstring

~~~text
Relative links and heading anchors in README, community files and docs/ resolve (offline).
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
