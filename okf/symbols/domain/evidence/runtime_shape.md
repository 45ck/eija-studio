---
type: Function
title: domain.evidence.runtime_shape
description: '`def runtime_shape(context: Context | None) -> RuntimeShape` in `domain/evidence`.'
resource: repo://src/eija_studio/domain/evidence.py#runtime_shape
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/evidence.py#runtime_shape
  title: domain/evidence.py
  hash_method: ast-v2
  sha256: 749564777ec7e8235ecaf252b50c90183748b121cebc0b63180b72e52ec92487
notes_baseline: 35bdcad9a338ad33286400a1bd5f1f368db4be849a42c7af27b5484301b2d223
---

# domain.evidence.runtime_shape

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/evidence`](/modules/domain/evidence.md) |
| Signature | `def runtime_shape(context: Context \| None) -> RuntimeShape` |
| Code | `repo://src/eija_studio/domain/evidence.py#runtime_shape` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.evidence.expected_shape](/symbols/domain/evidence/expected_shape.md) - The runtime matrix a receipt must cover under ``pack``: exactly ``model``'s states when it is known.
* [domain.formal.Context](/symbols/domain/formal/Context.md) - What the kernel itself knows about the CURRENT subject, beyond the technical dimensions.
* [domain.formal.RuntimeShape](/symbols/domain/formal/RuntimeShape.md) - What a runtime-matrix receipt for the current subject must cover: the pack's fixture actors and declared actions, and one of the allowed state sets (exactly th…
* [domain.pack.default_pack](/symbols/domain/pack/default_pack.md) - The configured pack, reread on every call and validated from a content-keyed cache.

## Referenced by

* [domain.evidence.assess_receipt](/symbols/domain/evidence/assess_receipt.md) - `def assess_receipt(receipt: dict[str, Any], subject: dict[str, Any], claim: str, kind: str, context: Context…` in `domain/evidence`.
<!-- okf:generated:end links -->
