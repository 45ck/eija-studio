---
type: Function
title: domain.models.canonical
description: Canonical JSON text (sorted keys, no whitespace, no NaN) for a value or pydantic model.
resource: repo://src/eija_studio/domain/models.py#canonical
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#canonical
  title: domain/models.py
  hash_method: ast-v1
  sha256: bca4f1ea07f3bdeb092537dff77c6ad20dc415f2c27ae88f6229226521c5315d
description_override: Canonical JSON text (sorted keys, no whitespace, no NaN) for a value or pydantic model.
---

# domain.models.canonical

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `def canonical(value: Any) -> str` |
| Code | `repo://src/eija_studio/domain/models.py#canonical` |
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Everything that is hashed goes through this so that equal meaning gives equal bytes.

<!-- okf:generated:begin links -->
## Referenced by

* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models` (the source has no docstring).
<!-- okf:generated:end links -->
