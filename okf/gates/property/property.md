---
type: Quality Gate
title: nox -s property
description: Hypothesis properties + stateful differential test, ci profile (derandomized, fast).
resource: repo://quality/sessions/property.py#property_tests
tags:
- gate
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/property.py#property_tests
  title: property.py
  hash_method: ast-v2
  sha256: efe32db58330f70509bc6fb13cb3e6a3445ebcf65f790ea305204e4576d817c1
notes_baseline: d1d62a32d37d9a221a16795b676294d06396da35c986c33b3030a7097b9a4e8d
---

# nox -s property

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s property` |
| Tiers | `full` |
| Session module | `repo://quality/sessions/property.py` |
| Code | `repo://quality/sessions/property.py#property_tests` |

## Docstring

~~~text
Hypothesis properties + stateful differential test, ci profile (derandomized, fast).
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
