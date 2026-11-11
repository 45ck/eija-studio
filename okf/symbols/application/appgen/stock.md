---
type: Function
title: application.appgen.stock
description: One valid object of each class a record refers to (ADR-0235), stored before the data cases run.
resource: repo://src/eija_studio/application/appgen.py#stock
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/appgen.py#stock
  title: application/appgen.py
  hash_method: ast-v2
  sha256: 3cd8e488d8b0a826e85036e9f8c935755ba721256120cbdb86077a00207e285e
notes_baseline: 2fca26a83649e13eafec82d06f002d425a516a72d2fe1d52c02ea3836c9e21e4
---

# application.appgen.stock

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/appgen`](/modules/application/appgen.md) |
| Signature | `def stock(data: DataModel) -> list[dict[str, object]]` |
| Code | `repo://src/eija_studio/application/appgen.py#stock` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
One valid object of each class a record refers to (ADR-0235), stored before the data cases run. Empty when no
association is built, so other oracles keep their exact bytes.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.data.references](/symbols/domain/data/references.md) - The record's reference fields, one per built association, in declaration order.

## Referenced by

* [application.appgen.data_cases](/symbols/application/appgen/data_cases.md) - Record values to create with, and `check_record`'s answer for each: a valid record, then each required value missing, each value of the wrong type, each text o…
* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
<!-- okf:generated:end links -->
