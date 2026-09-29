---
type: Quality Gate
title: nox -s property_deep
description: The same suite with random seeds and 10x examples; failures are saved under .hypothesis/.
resource: repo://quality/sessions/property.py#property_deep
tags:
- gate
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/property.py#property_deep
  title: property.py
  hash_method: ast-v2
  sha256: 3bce27ef58e6b6d84684ee307b3c35e60ff1449d9c00741403f322784c17d1e6
notes_baseline: 517955a3dd5c3745059109ba40a4694109c5cee100847cf3fa37673885953437
---

# nox -s property_deep

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s property_deep` |
| Tiers | `release` |
| Session module | `repo://quality/sessions/property.py` |
| Code | `repo://quality/sessions/property.py#property_deep` |

## Docstring

~~~text
The same suite with random seeds and 10x examples; failures are saved under .hypothesis/.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
