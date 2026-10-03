---
type: Quality Gate
title: nox -s coverage
description: Branch coverage of src/eija_studio with a ratcheted floor; reports go to reports/coverage/.
resource: repo://quality/sessions/quality.py#coverage
tags:
- gate
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/quality.py#coverage
  title: quality.py
  hash_method: ast-v2
  sha256: 415368d5bc9ec16ce7d101a575814527a87e1fed76b1fc01eebbaa921581e362
notes_baseline: b760bf174fcb5a87b356522e5d3b570295cb5453e10b744030740fc5cb12390d
---

# nox -s coverage

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s coverage` |
| Tiers | `full` |
| Session module | `repo://quality/sessions/quality.py` |
| Code | `repo://quality/sessions/quality.py#coverage` |

## Docstring

~~~text
Branch coverage of src/eija_studio with a ratcheted floor; reports go to reports/coverage/.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
