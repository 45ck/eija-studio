---
type: Class
title: application.witness_inspection.InspectionNavigation
description: Current artifacts have no complete witness-reference contract, so no link is emitted.
resource: repo://src/eija_studio/application/witness_inspection.py#InspectionNavigation
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/witness_inspection.py#InspectionNavigation
  title: application/witness_inspection.py
  hash_method: ast-sig-v1
  sha256: 1813d7c0ea465b61eef38ff2be9378bc296f32064c3bc2fe8e150429bfb0da8c
notes_baseline: b0e3047a1a2a614ffe02522f381d629c1d7169a82c68aedba1cd64015e3befdc
---

# application.witness_inspection.InspectionNavigation

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/witness_inspection`](/modules/application/witness_inspection.md) |
| Signature | `class InspectionNavigation(Contract)` |
| Code | `repo://src/eija_studio/application/witness_inspection.py#InspectionNavigation` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Current artifacts have no complete witness-reference contract, so no link is emitted.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `current_model` | `None` | `None` |
| `source` | `None` | `None` |
| `reasons` | `tuple[str, ...]` | `('EXPLICIT_REFERENCE_BINDING_NOT_PROVIDED',)` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [application.witness_inspection.InspectionRecord](/symbols/application/witness_inspection/InspectionRecord.md) - One exact JSON-pointer location within the deciding artifact, labelled by its known origin.
<!-- okf:generated:end links -->
