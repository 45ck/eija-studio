---
type: Function
title: domain.data.check_record
description: 'Validate a record''s values: its attributes with `check_values`, then each reference field, which must hold the id of a stored object of its class (`exists(class, id)`; ADR-0235).'
resource: repo://src/eija_studio/domain/data.py#check_record
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/data.py#check_record
  title: domain/data.py
  hash_method: ast-v2
  sha256: 5cc55e8ab2ce135e9d5e522b219c0e3eadd7d4352694c15478335f436aef38a9
notes_baseline: 2c6c86d8c243bf5ecfdb94740d59bc03b511ea83577ccb413392760fa01928ce
---

# domain.data.check_record

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/data`](/modules/domain/data.md) |
| Signature | `def check_record(data: DataModel, values: dict[str, Any], exists: Callable[[str, str], bool]) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/domain/data.py#check_record` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Validate a record's values: its attributes with `check_values`, then each reference field, which must hold the id
of a stored object of its class (`exists(class, id)`; ADR-0235). Returns the clean values.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.data.check_values](/symbols/domain/data/check_values.md) - Validate a record's values against its entity.
* [domain.data.references](/symbols/domain/data/references.md) - The record's reference fields, one per built association, in declaration order.
<!-- okf:generated:end links -->
