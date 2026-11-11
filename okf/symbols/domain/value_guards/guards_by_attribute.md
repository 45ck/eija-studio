---
type: Function
title: domain.value_guards.guards_by_attribute
description: Every value guard of the model, grouped by the attribute it reads, attributes in name order.
resource: repo://src/eija_studio/domain/value_guards.py#guards_by_attribute
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/value_guards.py#guards_by_attribute
  title: domain/value_guards.py
  hash_method: ast-v2
  sha256: 94098cd31701c460ce9f42a3b6d854e07d99ec27d948c527a86e1b9c864a414b
notes_baseline: aacc1fae97eb1ed9233784091e1508b4ca8e8101cf068ef93411f6ec48fb5a27
---

# domain.value_guards.guards_by_attribute

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/value_guards`](/modules/domain/value_guards.md) |
| Signature | `def guards_by_attribute(model: Workflow) -> dict[str, list[ValueGuard]]` |
| Code | `repo://src/eija_studio/domain/value_guards.py#guards_by_attribute` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Every value guard of the model, grouped by the attribute it reads, attributes in name order.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.ValueGuard](/symbols/domain/models/ValueGuard.md) - A UML guard over one of the record's values, such as ``[amount > 500]`` (issue #93, ADR-0234).
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [domain.value_guards.guard_problems](/symbols/domain/value_guards/guard_problems.md) - Codes for value guards that do not fit the data model's record class: no data model, an attribute the record does not have, or a constant of another type (or a…
* [domain.value_guards.valuations](/symbols/domain/value_guards/valuations.md) - One record's values for each combination of `points` over the guarded attributes, in a fixed order; a value of None is left out.
<!-- okf:generated:end links -->
