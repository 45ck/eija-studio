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
  sha256: 89eb4e8ed435f43d1e2d9ada4f257387fff59a9118f999645b4eb5b7f204b568
notes_baseline: 41b79a169345b3d89a8bc32e7328fbb2ba2f33972afff1bcbdbbcbd8813e5769
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

* [application.access.meeting](/symbols/application/access/meeting.md) - A record's values that meet every guard over values of these transitions (ADR-0234): {} when they have none, None when no values meet them all.
* [domain.value_guards.combinations](/symbols/domain/value_guards/combinations.md) - `valuations` over these guards, grouped by attribute.
<!-- okf:generated:end links -->
