---
type: Quality Gate
title: nox -s scxml_differential
description: Every oracle case gives the same outcome on an independent SCXML engine as on the kernel.
resource: repo://quality/sessions/xuml.py#scxml_differential
tags:
- gate
- full
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/xuml.py#scxml_differential
  title: xuml.py
  hash_method: ast-v2
  sha256: d3be42fb690a513f848afc6170cdd28d409689c4c55f1a3c8298dcd0ec0da1de
notes_baseline: 0f53df808c8920b5bae6be7420d1de2541e0d496ac6789f05e5772bf9bac0ee4
---

# nox -s scxml_differential

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s scxml_differential` |
| Tiers | `full`, `release` |
| Session module | `repo://quality/sessions/xuml.py` |
| Code | `repo://quality/sessions/xuml.py#scxml_differential` |

## Docstring

~~~text
Every oracle case gives the same outcome on an independent SCXML engine as on the kernel.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
