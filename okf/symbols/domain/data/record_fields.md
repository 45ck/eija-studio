---
type: Function
title: domain.data.record_fields
description: 'What a record holds: the record class''s attributes, then each reference field as text holding an object''s id.'
resource: repo://src/eija_studio/domain/data.py#record_fields
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/data.py#record_fields
  title: domain/data.py
  hash_method: ast-v2
  sha256: ef70870d0d0afc13d86cce296453ac3d22a7534e2e7f6a98bd76721616d3b41c
notes_baseline: 8851e7afe6636132c915304ba5922cb4aac3e6351d91935ce62d2a11cc46c944
---

# domain.data.record_fields

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/data`](/modules/domain/data.md) |
| Signature | `def record_fields(data: DataModel) -> tuple[Attribute, ...]` |
| Code | `repo://src/eija_studio/domain/data.py#record_fields` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
What a record holds: the record class's attributes, then each reference field as text holding an object's id.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.Attribute](/symbols/domain/data/Attribute.md) - `class Attribute(Contract)` in `domain/data`.
* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.data.REFERENCE_LENGTH](/symbols/domain/data/REFERENCE_LENGTH.md) - Constant `REFERENCE_LENGTH` in `domain/data`.
* [domain.data.references](/symbols/domain/data/references.md) - The record's reference fields, one per built association, in declaration order.

## Referenced by

* [application.appgen.data_cases](/symbols/application/appgen/data_cases.md) - Record values to create with, and `check_record`'s answer for each: a valid record, then each required value missing, each value of the wrong type, each text o…
* [domain.screens.check_screens](/symbols/domain/screens/check_screens.md) - Design problems, each with a stable code and the use case it is about.
* [domain.screens.default_screen](/symbols/domain/screens/default_screen.md) - The screen a use case gets when nobody designed one: `create` asks for every record field (attributes, then the references of built associations); an action sh…
<!-- okf:generated:end links -->
