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
  sha256: e246afad3932b4a6e7234cf21ce87915c9f41df8836a481ca602d93ea366d495
notes_baseline: f6cf9325eb5cd5ebcef49912a55bd113bb3779734983a70775418861da159ca1
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

* [`FormalVerdict`](/symbols/domain/evidence/FormalVerdict.md) (class) - The status of one evidence kind for the current subject, with the receipt that decided it.
* [`RUNTIME_MATRIX`](/symbols/domain/evidence/RUNTIME_MATRIX.md) (constant) - no docstring
* [`TECHNICAL_DIMENSIONS`](/symbols/domain/evidence/TECHNICAL_DIMENSIONS.md) (constant) - no docstring
* [`aggregate_formal`](/symbols/domain/evidence/aggregate_formal.md) (function) - Combine every receipt of one kind.
* [`aggregate_status`](/symbols/domain/evidence/aggregate_status.md) (function) - no docstring
* [`assess_formal_receipt`](/symbols/domain/evidence/assess_formal_receipt.md) (function) - Per-kind admissibility (ADR-0145): envelope checks in the runtime matrix's order, then the kind's own check.
* [`assess_receipt`](/symbols/domain/evidence/assess_receipt.md) (function) - no docstring
* [`combine`](/symbols/domain/evidence/combine.md) (function) - The status algebra: authenticated PASS and FAIL never average (CONFLICT); FAIL beats PASS-less states; STALE (a receipt…
* [`intact_artifact`](/symbols/domain/evidence/intact_artifact.md) (function) - The raw artifact of an authentic, hash-consistent, known-protocol receipt of this kind, whatever its subject.
* [`receipt_status`](/symbols/domain/evidence/receipt_status.md) (function) - One receipt's applicability by its OWN declared claim and kind; an unauthentic receipt is FAIL.

## Internal imports

* [`domain/evidence_kinds`](/modules/domain/evidence_kinds.md)
* [`domain/formal`](/modules/domain/formal.md)
* [`domain/models`](/modules/domain/models.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.evidence_kinds](/modules/domain/evidence_kinds.md) - The registry of evidence kinds the kernel can assess (ADR-0145).
* [domain.formal](/modules/domain/formal.md) - Primitives for per-kind admissibility of formal evidence (ADR-0145, ADR-0146).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).

## Referenced by

* [Assurance](/contexts/assurance.md) - Owns Subject dimensions, verification observations, admissibility and freshness
* [application.compiler](/modules/application/compiler.md) - Compiler: model → projections + impacts + obligations + computed review packet.
* [application.formal](/modules/application/formal.md) - Formal evidence in the application layer: seal what an adapter collected, and build the packet view.
* [domain.evidence.FormalVerdict](/symbols/domain/evidence/FormalVerdict.md) - The status of one evidence kind for the current subject, with the receipt that decided it.
* [domain.evidence.RUNTIME_MATRIX](/symbols/domain/evidence/RUNTIME_MATRIX.md) - Constant `RUNTIME_MATRIX` in `domain/evidence`.
* [domain.evidence.TECHNICAL_DIMENSIONS](/symbols/domain/evidence/TECHNICAL_DIMENSIONS.md) - Constant `TECHNICAL_DIMENSIONS` in `domain/evidence`.
* [domain.evidence.aggregate_formal](/symbols/domain/evidence/aggregate_formal.md) - Combine every receipt of one kind.
* [domain.evidence.aggregate_status](/symbols/domain/evidence/aggregate_status.md) - `def aggregate_status(receipts: list[dict[str, Any]], subject: dict[str, Any], authenticator: Callable[[dict[s…` in `domain/evidence`.
* [domain.evidence.assess_formal_receipt](/symbols/domain/evidence/assess_formal_receipt.md) - Per-kind admissibility (ADR-0145): envelope checks in the runtime matrix's order, then the kind's own check.
* [domain.evidence.assess_receipt](/symbols/domain/evidence/assess_receipt.md) - `def assess_receipt(receipt: dict[str, Any], subject: dict[str, Any], claim: str, kind: str, context: Context…` in `domain/evidence`.
* [domain.evidence.combine](/symbols/domain/evidence/combine.md) - The status algebra: authenticated PASS and FAIL never average (CONFLICT); FAIL beats PASS-less states; STALE (a receipt for another subject), then NOT_RUN (a p…
* [domain.evidence.intact_artifact](/symbols/domain/evidence/intact_artifact.md) - The raw artifact of an authentic, hash-consistent, known-protocol receipt of this kind, whatever its subject.
* [domain.evidence.receipt_status](/symbols/domain/evidence/receipt_status.md) - One receipt's applicability by its OWN declared claim and kind; an unauthentic receipt is FAIL.
<!-- okf:generated:end links -->
