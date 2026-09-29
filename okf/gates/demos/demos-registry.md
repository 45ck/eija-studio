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
  sha256: 672aa45a62cbdb9d21dc0ee576a1bd428e95996e32e854f748d3fced1ca5ee4f
notes_baseline: fc46a17cf7be637469ebf95ea9af6ce28cf6ba9659ea8f76eb841d1c2ad7effc
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
