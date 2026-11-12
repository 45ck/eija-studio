---
type: Function
title: domain.value_guards.points
description: Values of one attribute that stand for every value its guards can tell apart; None means no value.
resource: repo://src/eija_studio/domain/value_guards.py#points
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/value_guards.py#points
  title: domain/value_guards.py
  hash_method: ast-v2
  sha256: 239a7daad7ce63241a1494d9088f98c43678a008191e5bdf7ea1254d8ccc7351
notes_baseline: ed277e8011bf9dc53c8bebc3b84b651b615d7f2f16dcb3a1be0256f95610add8
---

# domain.value_guards.points

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/value_guards`](/modules/domain/value_guards.md) |
| Signature | `def points(guards: list[ValueGuard]) -> list[Any]` |
| Code | `repo://src/eija_studio/domain/value_guards.py#points` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Values of one attribute that stand for every value its guards can tell apart; None means no value.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.ValueGuard](/symbols/domain/models/ValueGuard.md) - A UML guard over one of the record's values, such as ``[amount > 500]`` (issue #93, ADR-0234).

## Referenced by

* [domain.value_guards.combinations](/symbols/domain/value_guards/combinations.md) - `valuations` over these guards, grouped by attribute.
<!-- okf:generated:end links -->
