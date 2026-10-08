---
type: Quality Gate
title: nox -s scxml_drift
description: The committed SCXML charts match the packs' models.
resource: repo://quality/sessions/xuml.py#scxml_drift
tags:
- gate
- fast
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/xuml.py#scxml_drift
  title: xuml.py
  hash_method: ast-v2
  sha256: ac8e1c64ec8a95c81ccd3913ef5754c24d04b5736f357d6ab9f0100baf366e02
notes_baseline: 3e88845bc58cf498f0ee86531b5a809439307a0e99d979964e33d45f5b67b0b9
---

# nox -s scxml_drift

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s scxml_drift` |
| Tiers | `fast`, `full` |
| Session module | `repo://quality/sessions/xuml.py` |
| Code | `repo://quality/sessions/xuml.py#scxml_drift` |

## Docstring

~~~text
The committed SCXML charts match the packs' models.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
