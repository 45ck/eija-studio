---
type: Class
title: application.witness_inspection.WitnessInspection
description: Supplemental record inspection; availability never changes the existing evidence status.
resource: repo://src/eija_studio/application/witness_inspection.py#WitnessInspection
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/witness_inspection.py#WitnessInspection
  title: application/witness_inspection.py
  hash_method: ast-sig-v1
  sha256: 03f2fcee16f02ac2db76a0fb147c875a00679ef124585de20fd7da9841a697e8
notes_baseline: 43636fdd26cf5b2f84138e825868e3fed5223152ea7790d22ab085b2ae01edc0
---

# application.witness_inspection.WitnessInspection

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/witness_inspection`](/modules/application/witness_inspection.md) |
| Signature | `class WitnessInspection(Contract)` |
| Code | `repo://src/eija_studio/application/witness_inspection.py#WitnessInspection` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Supplemental record inspection; availability never changes the existing evidence status.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `schema_version` | `Literal['eija.formal-inspection.v1']` | `'eija.formal-inspection.v1'` |
| `display_only` | `Literal[True]` | `True` |
| `scope` | `Literal['formal-record-inspection']` | `'formal-record-inspection'` |
| `kind` | `str` |  |
| `status` | `str` |  |
| `reasons` | `tuple[str, ...]` |  |
| `availability` | `Literal['available', 'unavailable']` |  |
| `availability_reasons` | `tuple[str, ...]` |  |
| `review` | `InspectionReview` |  |
| `receipt` | `InspectionReceipt \| None` | `None` |
| `artifact_json` | `str \| None` | `None` |
| `records` | `tuple[InspectionRecord, ...]` | `()` |
| `record_count` | `int` | `0` |
| `projection_reasons` | `tuple[str, ...]` | `()` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.witness_inspection.InspectionReceipt](/symbols/application/witness_inspection/InspectionReceipt.md) - Identity of the exact deciding intact receipt; its seal is deliberately not projected.
* [application.witness_inspection.InspectionRecord](/symbols/application/witness_inspection/InspectionRecord.md) - One exact JSON-pointer location within the deciding artifact, labelled by its known origin.
* [application.witness_inspection.InspectionReview](/symbols/application/witness_inspection/InspectionReview.md) - Full review identity; subject_json retains every subject field, including presentation.
* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [application.witness_inspection.inspect_verdict](/symbols/application/witness_inspection/inspect_verdict.md) - Project only the deciding receipt, retaining uncertainty and all recorded raw data without writes.
<!-- okf:generated:end links -->
