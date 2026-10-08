---
type: Quality Gate
title: nox -s interop_roundtrip
description: The committed UML exports are current, and every export reads back as exactly the model it came from.
resource: repo://quality/sessions/interop.py#interop_roundtrip
tags:
- gate
- fast
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/interop.py#interop_roundtrip
  title: interop.py
  hash_method: ast-v2
  sha256: 669f37a11e868513c0dff90a2d3b8b6c837802a098adf5fd03a1ad93e06d1d5b
notes_baseline: 1bb62196fcb51e4c7349521c06640709243233f5e69db9ec108649a3989fe900
---

# nox -s interop_roundtrip

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s interop_roundtrip` |
| Tiers | `fast`, `full` |
| Session module | `repo://quality/sessions/interop.py` |
| Code | `repo://quality/sessions/interop.py#interop_roundtrip` |

## Docstring

~~~text
The committed UML exports are current, and every export reads back as exactly the model it came from.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
