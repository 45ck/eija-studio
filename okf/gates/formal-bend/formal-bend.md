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
  sha256: 94b6277f4795d4b22051f7434a1e5a354b9bcd48da9546fea2b1b785a68e0f4b
notes_baseline: f9f64091741b8eb0c0afaa7fe97a9ae4ad7af4157f65ba287c0d8b4902db8975
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
