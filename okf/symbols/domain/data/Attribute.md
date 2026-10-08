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
  sha256: dcc5bdc68dfd6f0e0ce4308dcfe587eeeb610a2f233430401d770f97e3e3fe1a
notes_baseline: 371bf540ec15eb009b81ee6922b30b675fc281173152224445fca6a6101a664e
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
| `choices` | `tuple[str, ...]` | `Field(default=(), max_length=32)` |
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

* [domain.data.Attribute.coherent](/symbols/domain/data/Attribute.coherent.md) - `def coherent(self) -> Attribute` in `domain/data`.
* [domain.data.Entity](/symbols/domain/data/Entity.md) - `class Entity(Contract)` in `domain/data`.
<!-- okf:generated:end links -->
