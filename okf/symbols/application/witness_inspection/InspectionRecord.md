---
type: Class
title: application.witness_inspection.InspectionRecord
description: One exact JSON-pointer location within the deciding artifact, labelled by its known origin.
resource: repo://src/eija_studio/application/witness_inspection.py#InspectionRecord
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/witness_inspection.py#InspectionRecord
  title: application/witness_inspection.py
  hash_method: ast-sig-v1
  sha256: 07c61abe02e65ce68288440ce997d70a00e65f892365c1a2b2daf9058719e5f8
notes_baseline: 5881658f0aea587ae7514d458d18af184d160a65a766cfabedc07ae3d80358d0
---

# application.witness_inspection.InspectionRecord

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/witness_inspection`](/modules/application/witness_inspection.md) |
| Signature | `class InspectionRecord(Contract)` |
| Code | `repo://src/eija_studio/application/witness_inspection.py#InspectionRecord` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
One exact JSON-pointer location within the deciding artifact, labelled by its known origin.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `artifact_path` | `str` |  |
| `origin` | `Literal['counterexample', 'negative_control', 'diagnostic']` |  |
| `label` | `str` |  |
| `invariant` | `str \| None` |  |
| `raw_json` | `str` |  |
| `steps` | `tuple[InspectionStep, ...]` | `()` |
| `model` | `InspectionModel` | `InspectionModel()` |
| `navigation` | `InspectionNavigation` | `InspectionNavigation()` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.witness_inspection.InspectionModel](/symbols/application/witness_inspection/InspectionModel.md) - A supplied specimen, a validated projection of it, or an explicit absence of model data.
* [application.witness_inspection.InspectionNavigation](/symbols/application/witness_inspection/InspectionNavigation.md) - Current artifacts have no complete witness-reference contract, so no link is emitted.
* [application.witness_inspection.InspectionStep](/symbols/application/witness_inspection/InspectionStep.md) - An ordered literal recorded step.
* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [application.witness_inspection.WitnessInspection](/symbols/application/witness_inspection/WitnessInspection.md) - Supplemental record inspection; availability never changes the existing evidence status.
<!-- okf:generated:end links -->
