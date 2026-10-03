---
type: Class
title: application.witness_inspection.InspectionReview
description: Full review identity; subject_json retains every subject field, including presentation.
resource: repo://src/eija_studio/application/witness_inspection.py#InspectionReview
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/witness_inspection.py#InspectionReview
  title: application/witness_inspection.py
  hash_method: ast-sig-v1
  sha256: be937322afe274bcabd870f588210fdfd5d94ee69bc0472d444887bb2d7fa179
notes_baseline: 866d45fb0c0efd6ba1456f6eec3352fc3ac9c852a0c21bbe5b14bda5f7af4e17
---

# application.witness_inspection.InspectionReview

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/witness_inspection`](/modules/application/witness_inspection.md) |
| Signature | `class InspectionReview(Contract)` |
| Code | `repo://src/eija_studio/application/witness_inspection.py#InspectionReview` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Full review identity; subject_json retains every subject field, including presentation.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `case_id` | `str \| None` |  |
| `case_version` | `int \| None` |  |
| `scope` | `str \| None` |  |
| `subject_json` | `str` |  |
| `subject_hash` | `str` |  |
| `candidate_semantic_hash` | `str` |  |
| `pack_id` | `str \| None` |  |
| `pack_digest` | `str \| None` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [application.witness_inspection.WitnessInspection](/symbols/application/witness_inspection/WitnessInspection.md) - Supplemental record inspection; availability never changes the existing evidence status.
<!-- okf:generated:end links -->
