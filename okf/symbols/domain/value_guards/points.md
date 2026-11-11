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
  sha256: bfd0eec2c6417be939e2c4bbb821f57d36a955d37324aae7a074adf7172536c3
notes_baseline: a3879f61cbb055065917832e9237b29a3e60e92fb5db1587a7cf0c0bd9bd03c1
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
