---
type: Class
title: application.witness_inspection.InspectionReceipt
description: Identity of the exact deciding intact receipt; its seal is deliberately not projected.
resource: repo://src/eija_studio/application/witness_inspection.py#InspectionReceipt
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/witness_inspection.py#InspectionReceipt
  title: application/witness_inspection.py
  hash_method: ast-sig-v1
  sha256: c93113b1b74eba6aa297112ded6333b252dc17fb08d31e6d910797ae45e6b9e3
notes_baseline: e6c020e2f8a528cd2f7d7a53485e179c73484005b5215c83ecb329fa2a699ce5
---

# application.witness_inspection.InspectionReceipt

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/witness_inspection`](/modules/application/witness_inspection.md) |
| Signature | `class InspectionReceipt(Contract)` |
| Code | `repo://src/eija_studio/application/witness_inspection.py#InspectionReceipt` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Identity of the exact deciding intact receipt; its seal is deliberately not projected.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `id` | `str \| None` |  |
| `subject_json` | `str` |  |
| `artifact_hash` | `str \| None` |  |
| `producer` | `str \| None` |  |
| `method` | `str \| None` |  |
| `subject_matches_review` | `bool` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [application.witness_inspection.WitnessInspection](/symbols/application/witness_inspection/WitnessInspection.md) - Supplemental record inspection; availability never changes the existing evidence status.
* [application.witness_inspection.inspect_verdict](/symbols/application/witness_inspection/inspect_verdict.md) - Project only the deciding receipt, retaining uncertainty and all recorded raw data without writes.
<!-- okf:generated:end links -->
