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
  sha256: 652d520a8df9f66541ca323bddd5dc4531d101eae2b5657e427fc4dbfbbe69e5
notes_baseline: 85237abfa83c97e379881d5bc9ccbc0ee14aba32c78c5c597992fd3190b53e30
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
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
<!-- okf:generated:end links -->
