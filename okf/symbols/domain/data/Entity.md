---
type: Class
title: domain.data.Entity
description: '`class Entity(Contract)` in `domain/data`.'
resource: repo://src/eija_studio/domain/data.py#Entity
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/data.py#Entity
  title: domain/data.py
  hash_method: ast-sig-v1
  sha256: c018e3d8c63ec13388a620fcd9ed8468caf16dbcbab538822cb3d8ae7a4edca4
notes_baseline: f3d7743e83238f7141ffe1c0be508be8ffd1008f5bc0a68a7e4e30edb11d137a
---

# domain.data.Entity

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/data`](/modules/domain/data.md) |
| Signature | `class Entity(Contract)` |
| Code | `repo://src/eija_studio/domain/data.py#Entity` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `name` | `str` | `Field(pattern=NAME)` |
| `attributes` | `tuple[Attribute, ...]` | `Field(default=(), max_length=40)` |
| `description` | `str` | `Field(default='', max_length=300)` |

## Methods

* [`unique`](/symbols/domain/data/Entity.unique.md) - `def unique(self) -> Entity`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.Attribute](/symbols/domain/data/Attribute.md) - `class Attribute(Contract)` in `domain/data`.
* [domain.data.NAME](/symbols/domain/data/NAME.md) - Constant `NAME` in `domain/data`.
* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [domain.data.DataModel.entity](/symbols/domain/data/DataModel.entity.md) - `def entity(self, name: str) -> Entity` in `domain/data`.
* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.data.Entity.unique](/symbols/domain/data/Entity.unique.md) - `def unique(self) -> Entity` in `domain/data`.
* [domain.data.check_values](/symbols/domain/data/check_values.md) - Validate a record's values against its entity.
<!-- okf:generated:end links -->
