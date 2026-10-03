---
type: Quality Gate
title: nox -s community_files
description: Community files exist; CITATION.cff agrees with pyproject; roadmap covers every reserved ADR block.
resource: repo://quality/sessions/oss.py#community_files
tags:
- gate
- fast
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/oss.py#community_files
  title: oss.py
  hash_method: ast-v2
  sha256: e6540149cfe0cf3a81ac64acfe6611d3d023f2bb450622ecf8d18a27071ceca3
notes_baseline: 90e76f01f5b88173cbfd4e2f080a9d27e25752e90a87c45bade2f3f9efabfedb
---

# nox -s community_files

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s community_files` |
| Tiers | `fast`, `full` |
| Session module | `repo://quality/sessions/oss.py` |
| Code | `repo://quality/sessions/oss.py#community_files` |

## Docstring

~~~text
Community files exist; CITATION.cff agrees with pyproject; roadmap covers every reserved ADR block.

NOT_RUN (a skipped session, never a green one) when PyYAML (extra `docs`) is missing and the issue forms
could not be parsed; every other check still ran and its failures still fail the session.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
