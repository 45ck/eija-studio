---
type: Class
title: domain.screens.ScreenField
description: '`class ScreenField(Contract)` in `domain/screens`.'
resource: repo://src/eija_studio/domain/screens.py#ScreenField
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/screens.py#ScreenField
  title: domain/screens.py
  hash_method: ast-sig-v1
  sha256: d27e040539bb12b85bdf2282ed938f971a39368cb6738337014e1d560fd85f49
notes_baseline: 92b51b85d2a93d32cd985458d668d470f32e7f272215b40c59878b1ee4dad781
---

# domain.screens.ScreenField

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/screens`](/modules/domain/screens.md) |
| Signature | `class ScreenField(Contract)` |
| Code | `repo://src/eija_studio/domain/screens.py#ScreenField` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `attribute` | `str` | `Field(pattern=ATTRIBUTE_NAME)` |
| `label` | `str` | `Field(default='', max_length=60)` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.ATTRIBUTE_NAME](/symbols/domain/data/ATTRIBUTE_NAME.md) - Constant `ATTRIBUTE_NAME` in `domain/data`.
* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [domain.screens.Screen](/symbols/domain/screens/Screen.md) - `class Screen(Contract)` in `domain/screens`.
<!-- okf:generated:end links -->
