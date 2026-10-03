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
  sha256: 19d437dce3564a617d48f7810487a18c833f917aace76290f0b432f3e648b37a
notes_baseline: dd42f3cfa4789a875b88d3593de0b8c7198b26c2e1a651e660462d7e63e3acee
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
* [`expected_shape`](/symbols/domain/evidence/expected_shape.md) (function) - The runtime matrix a receipt must cover under ``pack``: exactly ``model``'s states when it is known.
* [`intact_artifact`](/symbols/domain/evidence/intact_artifact.md) (function) - The raw artifact of an authentic, hash-consistent, known-protocol receipt of this kind, whatever its subject.
* [`receipt_status`](/symbols/domain/evidence/receipt_status.md) (function) - One receipt's applicability by its OWN declared claim and kind; an unauthentic receipt is FAIL.
* [`runtime_shape`](/symbols/domain/evidence/runtime_shape.md) (function) - no docstring

## Internal imports

* [`domain/evidence_kinds`](/modules/domain/evidence_kinds.md)
* [`domain/formal`](/modules/domain/formal.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.evidence_kinds](/modules/domain/evidence_kinds.md) - The registry of evidence kinds the kernel can assess (ADR-0145).
* [domain.formal](/modules/domain/formal.md) - Primitives for per-kind admissibility of formal evidence (ADR-0145, ADR-0146).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [Assurance](/contexts/assurance.md) - Owns Subject dimensions, verification observations, admissibility and freshness
* [application.compiler](/modules/application/compiler.md) - Compiler: model → projections + impacts + obligations + computed review packet.
* [application.formal](/modules/application/formal.md) - Formal evidence in the application layer: seal what an adapter collected, and build the packet view.
* [application.witness_inspection](/modules/application/witness_inspection.md) - Immutable display projections of the deciding formal record, never new evidence or verdicts.
* [domain.evidence.FormalVerdict](/symbols/domain/evidence/FormalVerdict.md) - The status of one evidence kind for the current subject, with the receipt that decided it.
* [domain.evidence.RUNTIME_MATRIX](/symbols/domain/evidence/RUNTIME_MATRIX.md) - Constant `RUNTIME_MATRIX` in `domain/evidence`.
* [domain.evidence.TECHNICAL_DIMENSIONS](/symbols/domain/evidence/TECHNICAL_DIMENSIONS.md) - Constant `TECHNICAL_DIMENSIONS` in `domain/evidence`.
* [domain.evidence.aggregate_formal](/symbols/domain/evidence/aggregate_formal.md) - Combine every receipt of one kind.
* [domain.evidence.aggregate_status](/symbols/domain/evidence/aggregate_status.md) - `def aggregate_status(receipts: list[dict[str, Any]], subject: dict[str, Any], authenticator: Callable[[dict[s…` in `domain/evidence`.
* [domain.evidence.assess_formal_receipt](/symbols/domain/evidence/assess_formal_receipt.md) - Per-kind admissibility (ADR-0145): envelope checks in the runtime matrix's order, then the kind's own check.
* [domain.evidence.assess_receipt](/symbols/domain/evidence/assess_receipt.md) - `def assess_receipt(receipt: dict[str, Any], subject: dict[str, Any], claim: str, kind: str, context: Context…` in `domain/evidence`.
* [domain.evidence.combine](/symbols/domain/evidence/combine.md) - The status algebra: authenticated PASS and FAIL never average (CONFLICT); FAIL beats PASS-less states; STALE (a receipt for another subject), then NOT_RUN (a p…
* [domain.evidence.expected_shape](/symbols/domain/evidence/expected_shape.md) - The runtime matrix a receipt must cover under ``pack``: exactly ``model``'s states when it is known.
* [domain.evidence.intact_artifact](/symbols/domain/evidence/intact_artifact.md) - The raw artifact of an authentic, hash-consistent, known-protocol receipt of this kind, whatever its subject.
* [domain.evidence.receipt_status](/symbols/domain/evidence/receipt_status.md) - One receipt's applicability by its OWN declared claim and kind; an unauthentic receipt is FAIL.
* [domain.evidence.runtime_shape](/symbols/domain/evidence/runtime_shape.md) - `def runtime_shape(context: Context | None) -> RuntimeShape` in `domain/evidence`.
<!-- okf:generated:end links -->
