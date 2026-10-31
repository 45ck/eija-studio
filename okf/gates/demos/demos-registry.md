---
type: Quality Gate
title: nox -s demos_registry
description: Catalogue matches the code, REGISTRY.md is fresh, manifests are well formed.
resource: repo://quality/sessions/demos.py#demos_registry
tags:
- gate
- fast
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/demos.py#demos_registry
  title: demos.py
  hash_method: ast-v2
  sha256: 0102f8834f3e20428a60ad0edc268c7aff682837e5d66d7790d4ea91749a86b9
notes_baseline: 8ebf61150259e878c8b3ad196679c6d469b5e1d526a9c947245f981b830cbe71
---

# nox -s demos_registry

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s demos_registry` |
| Tiers | `fast`, `full` |
| Session module | `repo://quality/sessions/demos.py` |
| Code | `repo://quality/sessions/demos.py#demos_registry` |

## Docstring

~~~text
Catalogue matches the code, REGISTRY.md is fresh, manifests are well formed. No browser needed.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
