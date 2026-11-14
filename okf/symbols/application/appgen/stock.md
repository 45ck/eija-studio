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
  sha256: c788d6e735d9f31a6984c93edb0018dc0f927501f895b18ed2fc73b7357ebc44
notes_baseline: 79c66dd085d8a95140b3adfdbc706a45bad82196f58099792361d5a58488226b
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
* [application.appgen.object_cases](/symbols/application/appgen/object_cases.md) - Objects of each class a record refers to, created through the app (ADR-0235): a valid one, which starts in its lifecycle's initial state when the model gives i…
* [application.appgen.valid_values](/symbols/application/appgen/valid_values.md) - A valid record: a sample of each attribute, and each reference naming the first `stock` object of its class.
<!-- okf:generated:end links -->
