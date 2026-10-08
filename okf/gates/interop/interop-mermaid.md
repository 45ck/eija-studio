---
type: Quality Gate
title: nox -s interop_mermaid
description: Mermaid's own parser reads every Mermaid export as PlayIDE does; its negative controls are caught.
resource: repo://quality/sessions/interop.py#interop_mermaid
tags:
- gate
- full
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/interop.py#interop_mermaid
  title: interop.py
  hash_method: ast-v2
  sha256: 5f0ec04efa33ee9e264938541324d00e22a83911dea94a755c28c8a7abb8b4e6
notes_baseline: a5f25bebfa61e8bc4f7db7f9220acdddc768bbaa54cb779d18ddf1da83322062
---

# nox -s interop_mermaid

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s interop_mermaid` |
| Tiers | `full`, `release` |
| Session module | `repo://quality/sessions/interop.py` |
| Code | `repo://quality/sessions/interop.py#interop_mermaid` |

## Docstring

~~~text
Mermaid's own parser reads every Mermaid export as PlayIDE does; its negative controls are caught.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
