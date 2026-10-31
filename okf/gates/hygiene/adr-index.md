---
type: Quality Gate
title: nox -s adr_index
description: docs/adr/README.md index matches the ADR files; numbers unique; every record parses.
resource: repo://quality/sessions/hygiene.py#adr_index
tags:
- gate
- fast
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/hygiene.py#adr_index
  title: hygiene.py
  hash_method: ast-v2
  sha256: 9e77a7f1ecaa276c2f535fb6eb7b57dd5c157f5b6d7f56f9bb6e2afd36200798
notes_baseline: d6460f7c01395d12355b2cf966d0c08306c454fe43a3ad9bc7fcee2f6cdefb7d
---

# nox -s adr_index

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s adr_index` |
| Tiers | `fast`, `full` |
| Session module | `repo://quality/sessions/hygiene.py` |
| Code | `repo://quality/sessions/hygiene.py#adr_index` |

## Docstring

~~~text
docs/adr/README.md index matches the ADR files; numbers unique; every record parses.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
