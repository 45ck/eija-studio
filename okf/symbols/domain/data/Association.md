---
type: Class
title: domain.data.Association
description: '`class Association(Contract)` in `domain/data`.'
resource: repo://src/eija_studio/domain/data.py#Association
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/data.py#Association
  title: domain/data.py
  hash_method: ast-sig-v1
  sha256: 9f2925dc2281e0161958b5300653c28e6cb2b213930b4c98e31a6c725be9811a
notes_baseline: b453a9c0a86e44d7339575ce228a9422bbed268113b717e16f21df051416964a
---

# domain.data.Association

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/data`](/modules/domain/data.md) |
| Signature | `class Association(Contract)` |
| Code | `repo://src/eija_studio/domain/data.py#Association` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `source` | `str` | `Field(pattern=NAME)` |
| `target` | `str` | `Field(pattern=NAME)` |
| `kind` | `Literal['association', 'composition', 'aggregation']` | `'association'` |
| `role` | `str` | `Field(default='', max_length=40)` |
| `source_multiplicity` | `Multiplicity` | `'1'` |
| `target_multiplicity` | `Multiplicity` | `'0..*'` |
| `built` | `bool` | `False` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.Multiplicity](/symbols/domain/data/Multiplicity.md) - Type alias `Multiplicity` in `domain/data`.
* [domain.data.NAME](/symbols/domain/data/NAME.md) - Constant `NAME` in `domain/data`.
* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
<!-- okf:generated:end links -->
