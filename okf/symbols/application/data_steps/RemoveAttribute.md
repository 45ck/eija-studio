---
type: Class
title: application.data_steps.RemoveAttribute
description: '`class RemoveAttribute(Contract)` in `application/data_steps`.'
resource: repo://src/eija_studio/application/data_steps.py#RemoveAttribute
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/data_steps.py#RemoveAttribute
  title: application/data_steps.py
  hash_method: ast-sig-v1
  sha256: f091480b26345970a98a76d22de7fc5ee53f82b54968055f29d9d0e77de770b5
notes_baseline: 1e9d24137fdf3b6b5564cc3fc34555d10330136c799c1a205754be4ef82efc85
---

# application.data_steps.RemoveAttribute

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/data_steps`](/modules/application/data_steps.md) |
| Signature | `class RemoveAttribute(Contract)` |
| Code | `repo://src/eija_studio/application/data_steps.py#RemoveAttribute` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['remove_attribute']` |  |
| `entity` | `str` | `Field(pattern=NAME)` |
| `name` | `str` | `Field(pattern=ATTRIBUTE_NAME)` |
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
* [application.data_steps.describe_data](/symbols/application/data_steps/describe_data.md) - One line a person can check against the class diagram.
<!-- okf:generated:end links -->
