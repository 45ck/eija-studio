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
  hash_method: ast-v2
  sha256: d8aa96793b176d0dc4bbd35dd341e1d853493b1f53b8ea042df3063b976f6495
description_override: Canonical JSON text (sorted keys, no whitespace, no NaN) for a value or pydantic model.
notes_baseline: 64bc1b2dbf859863c53ed452ee491126840e4578d66b3c6e2ece6cff4088a360
---

# domain.models.canonical

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `def canonical(value: Any) -> str` |
| Code | `repo://src/eija_studio/domain/models.py#canonical` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Everything that is hashed goes through this so that equal meaning gives equal bytes.

<!-- okf:generated:begin links -->
## Referenced by

* [application.witness_inspection.inspect_verdict](/symbols/application/witness_inspection/inspect_verdict.md) - Project only the deciding receipt, retaining uncertainty and all recorded raw data without writes.
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models`.
<!-- okf:generated:end links -->
