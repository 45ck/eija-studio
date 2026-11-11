---
type: Function
title: domain.value_guards.combinations
description: '`valuations` over these guards, grouped by attribute.'
resource: repo://src/eija_studio/domain/value_guards.py#combinations
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/value_guards.py#combinations
  title: domain/value_guards.py
  hash_method: ast-v2
  sha256: fdb61decdf9dac959546151451f8bc924d752d7d0f7f238ff5e2fdc8b056dfa5
notes_baseline: ccf68d2bbf4ea2d14b0008745285474de34501db1f82bc9691110c98929cc296
---

# domain.value_guards.combinations

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/value_guards`](/modules/domain/value_guards.md) |
| Signature | `def combinations(grouped: dict[str, list[ValueGuard]]) -> list[dict[str, Any]] \| None` |
| Code | `repo://src/eija_studio/domain/value_guards.py#combinations` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
`valuations` over these guards, grouped by attribute.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.ValueGuard](/symbols/domain/models/ValueGuard.md) - A UML guard over one of the record's values, such as ``[amount > 500]`` (issue #93, ADR-0234).
* [domain.value_guards.MAX_VALUATIONS](/symbols/domain/value_guards/MAX_VALUATIONS.md) - Constant `MAX_VALUATIONS` in `domain/value_guards`.
* [domain.value_guards.points](/symbols/domain/value_guards/points.md) - Values of one attribute that stand for every value its guards can tell apart; None means no value.

## Referenced by

* [application.appgen.value_cases](/symbols/application/appgen/value_cases.md) - For each transition with guards over record values, an actor who may take it tries it on records holding every combination of values its guards can tell apart…
* [domain.value_guards.valuations](/symbols/domain/value_guards/valuations.md) - One record's values for each combination of `points` over the guarded attributes, in a fixed order; a value of None is left out.
<!-- okf:generated:end links -->
