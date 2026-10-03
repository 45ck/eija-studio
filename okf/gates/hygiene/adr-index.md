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
  sha256: 1086a70314aa33c4f3eac4981009e0853a0db724c5dfbca24e8328d6fe64e343
notes_baseline: 6962d0bf5491e69b77017b36eada594eeb08791c7d0f619c6e1de03dc5e473e6
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
