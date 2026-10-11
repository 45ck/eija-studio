---
type: Quality Gate
title: nox -s playide_activation
description: Observe real services, retained source identity and behavioral negative controls; never stamp source.
resource: repo://quality/sessions/activation.py#playide_activation
tags:
- gate
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/activation.py#playide_activation
  title: activation.py
  hash_method: ast-v2
  sha256: e54ea9c4b68a0c5fe0a708a4ab5e7cefdce1bfeade2aefdaa193d7563f47c131
notes_baseline: 4b5252c29d9b170e858d9632d20a962504294cb4a25023de951968590950bda4
---

# nox -s playide_activation

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s playide_activation` |
| Tiers | `full` |
| Session module | `repo://quality/sessions/activation.py` |
| Code | `repo://quality/sessions/activation.py#playide_activation` |

## Docstring

~~~text
Observe real services, retained source identity and behavioral negative controls; never stamp source.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
