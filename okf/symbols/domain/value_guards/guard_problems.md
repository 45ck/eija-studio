---
type: Function
title: domain.value_guards.guard_problems
description: 'Codes for value guards that do not fit the data model''s record class: no data model, an attribute the record does not have, or a constant of another type (or an ordering on text).'
resource: repo://src/eija_studio/domain/value_guards.py#guard_problems
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/value_guards.py#guard_problems
  title: domain/value_guards.py
  hash_method: ast-v2
  sha256: f7adef2c8002a827352eb2017148239fdf4edb5bb05917711c1d2c8ac5b8955f
notes_baseline: 9e80c565653139a0c86cef11851b1045a00969ed8e33e3383158b20da0651db7
---

# domain.value_guards.guard_problems

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/value_guards`](/modules/domain/value_guards.md) |
| Signature | `def guard_problems(model: Workflow, data: DataModel \| None) -> list[str]` |
| Code | `repo://src/eija_studio/domain/value_guards.py#guard_problems` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Codes for value guards that do not fit the data model's record class: no data model, an attribute the record
does not have, or a constant of another type (or an ordering on text). Empty when every guard fits.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.data.Entity](/symbols/domain/data/Entity.md) - `class Entity(Contract)` in `domain/data`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.value_guards.guards_by_attribute](/symbols/domain/value_guards/guards_by_attribute.md) - Every value guard of the model, grouped by the attribute it reads, attributes in name order.
<!-- okf:generated:end links -->
