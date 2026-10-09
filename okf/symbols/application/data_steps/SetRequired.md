---
type: Class
title: application.data_steps.SetRequired
description: '`class SetRequired(Contract)` in `application/data_steps`.'
resource: repo://src/eija_studio/application/data_steps.py#SetRequired
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/data_steps.py#SetRequired
  title: application/data_steps.py
  hash_method: ast-sig-v1
  sha256: 86473a408999b0b33bc532dee116219e035a11e398c3f5841751f7b033ace4ae
notes_baseline: a8b4a8d259f26b368f7a3d63bc19ba43ce318667e46dfc410944538595f1f3d9
---

# application.data_steps.SetRequired

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/data_steps`](/modules/application/data_steps.md) |
| Signature | `class SetRequired(Contract)` |
| Code | `repo://src/eija_studio/application/data_steps.py#SetRequired` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['set_required']` |  |
| `entity` | `str` | `Field(pattern=NAME)` |
| `name` | `str` | `Field(pattern=ATTRIBUTE_NAME)` |
| `required` | `bool` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.ATTRIBUTE_NAME](/symbols/domain/data/ATTRIBUTE_NAME.md) - Constant `ATTRIBUTE_NAME` in `domain/data`.
* [domain.data.NAME](/symbols/domain/data/NAME.md) - Constant `NAME` in `domain/data`.
* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [application.data_steps.DATA_EDITS](/symbols/application/data_steps/DATA_EDITS.md) - Constant `DATA_EDITS` in `application/data_steps`.
* [application.data_steps.DataEdit](/symbols/application/data_steps/DataEdit.md) - Type alias `DataEdit` in `application/data_steps`.
* [application.data_steps.DataStep](/symbols/application/data_steps/DataStep.md) - Type alias `DataStep` in `application/data_steps`.
<!-- okf:generated:end links -->
