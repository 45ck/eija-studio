---
type: Quality Gate
title: nox -s architecture
description: 'import-linter: layer order, vendor-free domain and application, adapters wired only by bootstrap.'
resource: repo://quality/sessions/quality.py#architecture
tags:
- gate
- fast
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/quality.py#architecture
  title: quality.py
  hash_method: ast-v2
  sha256: 85e34582ac832c92c0432ab911f0acb41c0da680d832bdb035309421c569df36
notes_baseline: 0397f08c8ca0845bb26715c2ceca5918b5daa81695d7eb4ab60067a5dd1d2e67
---

# nox -s architecture

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s architecture` |
| Tiers | `fast`, `full` |
| Session module | `repo://quality/sessions/quality.py` |
| Code | `repo://quality/sessions/quality.py#architecture` |

## Docstring

~~~text
import-linter: layer order, vendor-free domain and application, adapters wired only by bootstrap.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
