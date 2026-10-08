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
  sha256: c928a24a67d0ef410bd42687100e6131bb59b4ff5e282d883d4996dc537449d4
notes_baseline: 5f8c31d7ec50e721cb51af02fb521e20a9346915f50870d6f7788957ca136279
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
