---
type: Function
title: domain.data.references
description: The record's reference fields, one per built association, in declaration order.
resource: repo://src/eija_studio/domain/data.py#references
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/data.py#references
  title: domain/data.py
  hash_method: ast-v2
  sha256: 3aa95961f73d788e722ac9b4ba238975b31417aa2658b95f9deb9a961bf9d8d2
notes_baseline: 2fd99ae64564893e3b10ea963ed8035fc88c1a567847a4157d7aca94a5a53f3d
---

# domain.data.references

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/data`](/modules/domain/data.md) |
| Signature | `def references(data: DataModel \| None) -> list[Reference]` |
| Code | `repo://src/eija_studio/domain/data.py#references` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The record's reference fields, one per built association, in declaration order. Empty when nothing is built.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.data.Reference](/symbols/domain/data/Reference.md) - A built to-one association seen from the record: the field `name` holds the id of a stored `target` object.

## Referenced by

* [application.appgen.data_cases](/symbols/application/appgen/data_cases.md) - Record values to create with, and `check_record`'s answer for each: a valid record, then each required value missing, each value of the wrong type, each text o…
* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
* [application.appgen.stock](/symbols/application/appgen/stock.md) - One valid object of each class a record refers to (ADR-0235), stored before the data cases run.
* [application.class_build.class_build](/symbols/application/class_build/class_build.md) - Which classes and associations the built app stores and checks, and what to consider about the rest.
* [domain.data.check_record](/symbols/domain/data/check_record.md) - Validate a record's values: its attributes with `check_values`, then each reference field, which must hold the id of a stored object of its class (`exists(clas…
* [domain.data.record_fields](/symbols/domain/data/record_fields.md) - What a record holds: the record class's attributes, then each reference field as text holding an object's id.
<!-- okf:generated:end links -->
