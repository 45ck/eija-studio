---
type: Class
title: domain.data.Attribute
description: '`class Attribute(Contract)` in `domain/data`.'
resource: repo://src/eija_studio/domain/data.py#Attribute
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/data.py#Attribute
  title: domain/data.py
  hash_method: ast-sig-v1
  sha256: 9b66e77d11a3c7a3162a996904dbe15eb9d6000b2563174a5daac0c7fe354a1c
notes_baseline: e6b4c50cf90dd8304d74378a6dba3f62be7426011a4797ac5c67188e5018d995
---

# domain.data.Attribute

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/data`](/modules/domain/data.md) |
| Signature | `class Attribute(Contract)` |
| Code | `repo://src/eija_studio/domain/data.py#Attribute` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `name` | `str` | `Field(pattern=ATTRIBUTE_NAME)` |
| `type` | `FieldType` |  |
| `required` | `bool` | `False` |
| `choices` | `tuple[Annotated[str, Field(min_length=1, max_length=60)], ...]` | `Field(default=(), max_length=32)` |
| `max_length` | `int` | `Field(default=200, ge=1, le=5000)` |
| `description` | `str` | `Field(default='', max_length=300)` |

## Methods

* [`coherent`](/symbols/domain/data/Attribute.coherent.md) - `def coherent(self) -> Attribute`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.ATTRIBUTE_NAME](/symbols/domain/data/ATTRIBUTE_NAME.md) - Constant `ATTRIBUTE_NAME` in `domain/data`.
* [domain.data.FieldType](/symbols/domain/data/FieldType.md) - Type alias `FieldType` in `domain/data`.
* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [application.data_steps.AddAttribute](/symbols/application/data_steps/AddAttribute.md) - `class AddAttribute(Contract)` in `application/data_steps`.
* [domain.data.Attribute.coherent](/symbols/domain/data/Attribute.coherent.md) - `def coherent(self) -> Attribute` in `domain/data`.
* [domain.data.Entity](/symbols/domain/data/Entity.md) - `class Entity(Contract)` in `domain/data`.
<!-- okf:generated:end links -->
