---
type: Function
title: application.appgen.valid_values
description: 'A valid record: a sample of each attribute, and each reference naming the first `stock` object of its class.'
resource: repo://src/eija_studio/application/appgen.py#valid_values
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/appgen.py#valid_values
  title: application/appgen.py
  hash_method: ast-v2
  sha256: c2cf067f9ca3c1212796ec0b2c09ab161f490ab053d0d7ddc8ed6572b9df105f
notes_baseline: d8bdc63b3e5234bdd3cdebfbf65ba1b5edb95cd1dca6985628a889092e20152b
---

# application.appgen.valid_values

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/appgen`](/modules/application/appgen.md) |
| Signature | `def valid_values(data: DataModel \| None) -> dict[str, object]` |
| Code | `repo://src/eija_studio/application/appgen.py#valid_values` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
A valid record: a sample of each attribute, and each reference naming the first `stock` object of its class.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.appgen.stock](/symbols/application/appgen/stock.md) - One valid object of each class a record refers to (ADR-0235), stored before the data cases run.
* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.data.references](/symbols/domain/data/references.md) - The record's reference fields, one per built association, in declaration order.

## Referenced by

* [application.appgen.data_cases](/symbols/application/appgen/data_cases.md) - Record values to create with, and `check_record`'s answer for each: a valid record, then each required value missing, each value of the wrong type, each text o…
* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
<!-- okf:generated:end links -->
