---
type: Class
title: application.witness_inspection.InspectionModel
description: A supplied specimen, a validated projection of it, or an explicit absence of model data.
resource: repo://src/eija_studio/application/witness_inspection.py#InspectionModel
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/witness_inspection.py#InspectionModel
  title: application/witness_inspection.py
  hash_method: ast-sig-v1
  sha256: 5d3523ea894fbc1ff96325798b5e1f2329d895c4fb11ca8f1e167afe3d731844
notes_baseline: c105b5e348fded880e268818cfd7ebea8bfcb02c756f2c12bb7dc106b856b1db
---

# application.witness_inspection.InspectionModel

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/witness_inspection`](/modules/application/witness_inspection.md) |
| Signature | `class InspectionModel(Contract)` |
| Code | `repo://src/eija_studio/application/witness_inspection.py#InspectionModel` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
A supplied specimen, a validated projection of it, or an explicit absence of model data.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `availability` | `Literal['valid_workflow', 'raw_invalid', 'not_provided']` | `'not_provided'` |
| `slot` | `str \| None` | `None` |
| `supplied_semantic_hash` | `str \| None` | `None` |
| `computed_semantic_hash` | `str \| None` | `None` |
| `raw_json` | `str \| None` | `None` |
| `workflow` | `Workflow \| None` | `None` |
| `validation_errors` | `tuple[str, ...]` | `()` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [application.witness_inspection.InspectionRecord](/symbols/application/witness_inspection/InspectionRecord.md) - One exact JSON-pointer location within the deciding artifact, labelled by its known origin.
<!-- okf:generated:end links -->
