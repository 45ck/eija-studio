---
type: Function
title: application.appgen.data_cases
description: 'Record values to create with, and `check_values`'' answer for each: a valid record, then each required value missing, each value of the wrong type, each text one character too long, an undeclared choice and an unknown fi…'
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
  sha256: 7ac57ab6ceda84c27b70983cbdc97c14a796842f26d5ca692d839c4913b5761e
notes_baseline: 3f022638ad05db7c5e0d54679443a06cb4bc888a0ec6184777dac0c3c161d889
---

# application.appgen.data_cases

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/appgen`](/modules/application/appgen.md) |
| Signature | `def data_cases(pack: Pack, data: DataModel) -> list[dict[str, object]]` |
| Code | `repo://src/eija_studio/application/appgen.py#data_cases` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Record values to create with, and `check_values`' answer for each: a valid record, then each required value
missing, each value of the wrong type, each text one character too long, an undeclared choice and an unknown field.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.appgen.absent](/symbols/application/appgen/absent.md) - A name guaranteed not to be in `taken`, so a negative case can never collide with a declared one.
* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
<!-- okf:generated:end links -->
