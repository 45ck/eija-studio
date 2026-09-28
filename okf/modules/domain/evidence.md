---
type: Module
title: domain.evidence
description: Compatibility is computed.
resource: repo://src/eija_studio/domain/evidence.py
tags:
- module
- domain
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/evidence.py
  title: domain/evidence.py
  hash_method: ast-api-v1
  sha256: 8ed223a2515c9b6abaef0d99210c90d83a6ce34f27185b0975eaf50c73064dcc
---

# domain.evidence

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | domain |
| Code | `repo://src/eija_studio/domain/evidence.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Compatibility is computed. A supplied green status is never sufficient.
~~~

## Public symbols

* [`TECHNICAL_DIMENSIONS`](/symbols/domain/evidence/TECHNICAL_DIMENSIONS.md) (constant) - no docstring
* [`aggregate_status`](/symbols/domain/evidence/aggregate_status.md) (function) - no docstring
* [`assess_receipt`](/symbols/domain/evidence/assess_receipt.md) (function) - no docstring

## Internal imports

* [`domain/models`](/modules/domain/models.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).

## Referenced by

* [Assurance](/contexts/assurance.md) - Owns Subject dimensions, verification observations, admissibility and freshness
* [application.compiler](/modules/application/compiler.md) - Compiler: model → projections + impacts + obligations + computed review packet.
* [domain.evidence.TECHNICAL_DIMENSIONS](/symbols/domain/evidence/TECHNICAL_DIMENSIONS.md) - `TECHNICAL_DIMENSIONS = ('semantic', 'implementation', 'policy', 'environment', 'harness')` in `domain/evidence` (the source has no docstring).
* [domain.evidence.aggregate_status](/symbols/domain/evidence/aggregate_status.md) - `def aggregate_status(receipts: list[dict], subject: dict, authenticator) -> str` in `domain/evidence` (the source has no docstring).
* [domain.evidence.assess_receipt](/symbols/domain/evidence/assess_receipt.md) - `def assess_receipt(receipt: dict, subject: dict, claim: str, kind: str) -> str` in `domain/evidence` (the source has no docstring).
<!-- okf:generated:end links -->
