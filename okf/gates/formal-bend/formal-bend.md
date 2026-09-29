---
type: Quality Gate
title: nox -s formal_bend
description: 'The complete Bend evidence: proof, per-law attribution, negative controls, conformance.'
resource: repo://quality/sessions/formal_bend.py#formal_bend
tags:
- gate
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/formal_bend.py#formal_bend
  title: formal_bend.py
  hash_method: ast-v2
  sha256: b65a1a1688945ec30bec4bf35b7ca137c2cf9c68567592b7b2370f0421390580
notes_baseline: fe840b1b0abba8570b9eb58e54ff661e65089f9b1fed83c4720a755c0efa77c6
---

# nox -s formal_bend

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s formal_bend` |
| Tiers | `release` |
| Session module | `repo://quality/sessions/formal_bend.py` |
| Code | `repo://quality/sessions/formal_bend.py#formal_bend` |

## Docstring

~~~text
The complete Bend evidence: proof, per-law attribution, negative controls, conformance.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
