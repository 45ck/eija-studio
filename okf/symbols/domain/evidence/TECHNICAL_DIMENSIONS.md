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
  hash_method: ast-v2
  sha256: c91b1314a884cbd51f594af06cd656a92f4dd632c692a0a4b25da45b3d027948
description_override: 'The five subject dimensions an evidence receipt must match: semantic, implementation, policy, environment, harness.'
notes_baseline: 1c5487da1ab710504cca43bcabe22e5e973201c1da87b0d71b70a03dd75acaec
---

# domain.evidence.TECHNICAL_DIMENSIONS

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`domain/evidence`](/modules/domain/evidence.md) |
| Signature | `TECHNICAL_DIMENSIONS = ('semantic', 'implementation', 'policy', 'environment', 'harness')` |
| Code | `repo://src/eija_studio/domain/evidence.py#TECHNICAL_DIMENSIONS` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Presentation (layout) is deliberately excluded from runtime applicability but included in the exact decision subject, so a layout change keeps domain evidence but forces a fresh decision.

<!-- okf:generated:begin links -->
## Referenced by

* [domain.evidence.assess_receipt](/symbols/domain/evidence/assess_receipt.md) - `def assess_receipt(receipt: dict[str, Any], subject: dict[str, Any], claim: str, kind: str, context: Context…` in `domain/evidence`.
<!-- okf:generated:end links -->
