---
type: Class
title: application.data_steps.AddAttribute
description: '`class AddAttribute(Contract)` in `application/data_steps`.'
resource: repo://src/eija_studio/application/data_steps.py#AddAttribute
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/data_steps.py#AddAttribute
  title: application/data_steps.py
  hash_method: ast-sig-v1
  sha256: 8053f4f1aaf8dc20e81778c28a4ab59c7ff977b306fe2c1652973f6fb59c091d
notes_baseline: 752e4cadb30cfddf91c5702385e5f9f391c9d206a2b19c50a2e392776b5cfe3f
---

# application.data_steps.AddAttribute

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/data_steps`](/modules/application/data_steps.md) |
| Signature | `class AddAttribute(Contract)` |
| Code | `repo://src/eija_studio/application/data_steps.py#AddAttribute` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['add_attribute']` |  |
| `entity` | `str` | `Field(pattern=NAME)` |
| `attribute` | `Attribute` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.Attribute](/symbols/domain/data/Attribute.md) - `class Attribute(Contract)` in `domain/data`.
* [domain.data.NAME](/symbols/domain/data/NAME.md) - Constant `NAME` in `domain/data`.
* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [application.data_steps.DATA_EDITS](/symbols/application/data_steps/DATA_EDITS.md) - Constant `DATA_EDITS` in `application/data_steps`.
* [application.data_steps.DataEdit](/symbols/application/data_steps/DataEdit.md) - Type alias `DataEdit` in `application/data_steps`.
* [application.data_steps.DataStep](/symbols/application/data_steps/DataStep.md) - Type alias `DataStep` in `application/data_steps`.
* [application.data_steps.describe_data](/symbols/application/data_steps/describe_data.md) - One line a person can check against the class diagram.
<!-- okf:generated:end links -->
