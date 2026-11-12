---
type: Function
title: application.appgen.data_cases
description: 'Record values to create with, and `check_record`''s answer for each: a valid record, then each required value missing, each value of the wrong type, each text one character too long, an undeclared choice and an unknown f…'
resource: repo://src/eija_studio/application/appgen.py#data_cases
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/appgen.py#data_cases
  title: application/appgen.py
  hash_method: ast-v2
  sha256: 7edf2c45f71e303e1714afec6ce7a160f61556eecf6aa7ccd56054cb799ccdf6
notes_baseline: b622545c47057dee597bb881bc961db0ed416c5c48526071aa1ed8e8df361cee
---

# application.appgen.data_cases

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/appgen`](/modules/application/appgen.md) |
| Signature | `def data_cases(pack: Pack, data: DataModel, model: Workflow \| None=None) -> list[dict[str, object]]` |
| Code | `repo://src/eija_studio/application/appgen.py#data_cases` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Record values to create with, and `check_record`'s answer for each: a valid record, then each required value
missing, each value of the wrong type, each text one character too long, an undeclared choice and an unknown field,
then each reference field missing, not an id and naming no stored object (with the `stock` objects stored).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.appgen.absent](/symbols/application/appgen/absent.md) - A name guaranteed not to be in `taken`, so a negative case can never collide with a declared one.
* [application.appgen.stock](/symbols/application/appgen/stock.md) - One valid object of each class a record refers to (ADR-0235), stored before the data cases run.
* [application.appgen.valid_values](/symbols/application/appgen/valid_values.md) - A valid record: a sample of each attribute, and each reference naming the first `stock` object of its class.
* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.data.record_fields](/symbols/domain/data/record_fields.md) - What a record holds: the record class's attributes, then each reference field as text holding an object's id.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
<!-- okf:generated:end links -->
