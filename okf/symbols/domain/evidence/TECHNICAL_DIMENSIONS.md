---
type: Constant
title: domain.evidence.TECHNICAL_DIMENSIONS
description: 'The five subject dimensions an evidence receipt must match: semantic, implementation, policy, environment, harness.'
resource: repo://src/eija_studio/domain/evidence.py#TECHNICAL_DIMENSIONS
tags:
- symbol
- domain
- constant
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/evidence.py#TECHNICAL_DIMENSIONS
  title: domain/evidence.py
  hash_method: ast-v1
  sha256: ce194559573de513ef3b6e5beb5ea3b4519369658ee25507ebdaf6a9825df5bd
description_override: 'The five subject dimensions an evidence receipt must match: semantic, implementation, policy, environment, harness.'
---

# domain.evidence.TECHNICAL_DIMENSIONS

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`domain/evidence`](/modules/domain/evidence.md) |
| Signature | `TECHNICAL_DIMENSIONS = ('semantic', 'implementation', 'policy', 'environment', 'harness')` |
| Code | `repo://src/eija_studio/domain/evidence.py#TECHNICAL_DIMENSIONS` |
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Presentation (layout) is deliberately excluded from runtime applicability but included in the exact decision subject, so a layout change keeps domain evidence but forces a fresh decision.

<!-- okf:generated:begin links -->
## Referenced by

* [domain.evidence.assess_receipt](/symbols/domain/evidence/assess_receipt.md) - `def assess_receipt(receipt: dict, subject: dict, claim: str, kind: str) -> str` in `domain/evidence` (the source has no docstring).
<!-- okf:generated:end links -->
