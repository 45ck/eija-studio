---
type: Class
title: application.witness_inspection.InspectionStep
description: An ordered literal recorded step.
resource: repo://src/eija_studio/application/witness_inspection.py#InspectionStep
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/witness_inspection.py#InspectionStep
  title: application/witness_inspection.py
  hash_method: ast-sig-v1
  sha256: 2f5dd35208fb478885b02bfbb1a73d6e2128b73f34ea52a90556aa25a5b22ca5
notes_baseline: c3fd00d860398191ea1ae556cb2f62655342e31ed9bce67fc96498da5f954514
---

# application.witness_inspection.InspectionStep

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/witness_inspection`](/modules/application/witness_inspection.md) |
| Signature | `class InspectionStep(Contract)` |
| Code | `repo://src/eija_studio/application/witness_inspection.py#InspectionStep` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
An ordered literal recorded step. No action-name or execution inference is performed.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `index` | `int` |  |
| `raw_json` | `str` |  |
| `text` | `str \| None` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [application.witness_inspection.InspectionRecord](/symbols/application/witness_inspection/InspectionRecord.md) - One exact JSON-pointer location within the deciding artifact, labelled by its known origin.
<!-- okf:generated:end links -->
