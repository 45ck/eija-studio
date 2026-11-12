---
type: Quality Gate
title: nox -s conformance_divergence
description: 'Seeded divergence on library-loan and the feature variants: every one caught by behaviour, or refused.'
resource: repo://quality/sessions/conformance.py#conformance_divergence
tags:
- gate
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/conformance.py#conformance_divergence
  title: conformance.py
  hash_method: ast-v2
  sha256: 3032e6176bba0d3795588cd8881aae96b88bf5adb6d058a16ced102257218a0d
notes_baseline: 351b1777f5ecec9a6034fb6c58977c0a92abff56389af9643efdb6405b0fd94f
---

# nox -s conformance_divergence

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s conformance_divergence` |
| Tiers | `full` |
| Session module | `repo://quality/sessions/conformance.py` |
| Code | `repo://quality/sessions/conformance.py#conformance_divergence` |

## Docstring

~~~text
Seeded divergence on library-loan and the feature variants: every one caught by behaviour, or refused.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
