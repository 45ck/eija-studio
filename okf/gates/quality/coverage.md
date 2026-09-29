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
  sha256: 73fc08848737a24b7896e18bcfb227a8e87c507cdff1833072481ec6d0435205
notes_baseline: dd9f9f92cfd25e9a1be4c0add81f18b968bc62813d79beb3b4741f6c4c15b812
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
