---
type: Class
title: domain.models.ValueGuard
description: 'A UML guard over one of the record''s values, such as ``[amount > 500]`` (issue #93, ADR-0234).'
resource: repo://src/eija_studio/domain/models.py#ValueGuard
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#ValueGuard
  title: domain/models.py
  hash_method: ast-sig-v1
  sha256: c9ceac65a2d39cb2621c54c380d069186426d95899da6bf2a11e87109e1c61a1
notes_baseline: a797b6f2e2103f9eac0c847ace9c43557adbe278dedd45248e7e9ccad49a5a0c
---

# domain.models.ValueGuard

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `class ValueGuard(Contract)` |
| Code | `repo://src/eija_studio/domain/models.py#ValueGuard` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
A UML guard over one of the record's values, such as ``[amount > 500]`` (issue #93, ADR-0234). The transition
fires only when it holds. A value that is missing, or of another kind, never satisfies it (fail closed).
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `attribute` | `str` | `Field(pattern='^[a-z][a-zA-Z0-9_]{0,39}$')` |
| `op` | `Comparison` |  |
| `value` | `StrictBool \| StrictInt \| StrictFloat \| StrictStr` |  |

## Methods

* [`comparable`](/symbols/domain/models/ValueGuard.comparable.md) - `def comparable(self) -> ValueGuard`
* [`holds`](/symbols/domain/models/ValueGuard.holds.md) - `def holds(self, values: dict[str, Any]) -> bool`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Comparison](/symbols/domain/models/Comparison.md) - Type alias `Comparison` in `domain/models`.
* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [application.appgen.value_cases](/symbols/application/appgen/value_cases.md) - For each transition with guards over record values, an actor who may take it tries it on records holding every combination of values its guards can tell apart…
* [domain.models.Transition.admits](/symbols/domain/models/Transition.admits.md) - The first condition these record values fail, or None when the transition's conditions all hold.
* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models`.
* [domain.models.ValueGuard.comparable](/symbols/domain/models/ValueGuard.comparable.md) - `def comparable(self) -> ValueGuard` in `domain/models`.
* [domain.models.ValueGuard.holds](/symbols/domain/models/ValueGuard.holds.md) - `def holds(self, values: dict[str, Any]) -> bool` in `domain/models`.
* [domain.models.guard_keys](/symbols/domain/models/guard_keys.md) - Value guards as a set compared by their JSON, as the semantic hash compares them.
* [domain.value_guards.combinations](/symbols/domain/value_guards/combinations.md) - `valuations` over these guards, grouped by attribute.
* [domain.value_guards.guards_by_attribute](/symbols/domain/value_guards/guards_by_attribute.md) - Every value guard of the model, grouped by the attribute it reads, attributes in name order.
* [domain.value_guards.points](/symbols/domain/value_guards/points.md) - Values of one attribute that stand for every value its guards can tell apart; None means no value.
<!-- okf:generated:end links -->
