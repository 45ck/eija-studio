---
type: Function
title: domain.models.iso_date
description: The date a YYYY-MM-DD string names, or None.
resource: repo://src/eija_studio/domain/models.py#iso_date
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#iso_date
  title: domain/models.py
  hash_method: ast-v2
  sha256: 1036449436d3f7d374c11c63e4a65d4f8e62249f14919b2e00bbee42a1cd7ed2
notes_baseline: d39115924a7a999176585c40140fca697165bd8c24932a92d135980ac48bbe36
---

# domain.models.iso_date

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `def iso_date(text: str) -> date \| None` |
| Code | `repo://src/eija_studio/domain/models.py#iso_date` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The date a YYYY-MM-DD string names, or None. ISO dates compare as text in date order.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [domain.models.ValueGuard.comparable](/symbols/domain/models/ValueGuard.comparable.md) - `def comparable(self) -> ValueGuard` in `domain/models`.
* [domain.models.ValueGuard.holds](/symbols/domain/models/ValueGuard.holds.md) - `def holds(self, values: dict[str, Any]) -> bool` in `domain/models`.
<!-- okf:generated:end links -->
