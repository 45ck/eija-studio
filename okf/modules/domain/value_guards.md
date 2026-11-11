---
type: Module
title: domain.value_guards
description: 'Guards over a record''s values (issue #93, ADR-0234): which values can decide them, and whether they fit the data model.'
resource: repo://src/eija_studio/domain/value_guards.py
tags:
- module
- domain
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/value_guards.py
  title: domain/value_guards.py
  hash_method: ast-api-v1
  sha256: 37f48de27c10cfc5839117e66a4fec6161f7b7ed388b0206e877597409467703
notes_baseline: 1edb7ed5e8dccf1c436c0fc02742eca9386fca66ac3acf2c9376980333b29059
---

# domain.value_guards

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | domain |
| Code | `repo://src/eija_studio/domain/value_guards.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Guards over a record's values (issue #93, ADR-0234): which values can decide them, and whether they fit the data model.

A guard such as ``[amount > 500]`` compares one attribute of the record class with a constant. Whether it holds
depends only on which side of each constant a value falls, so a finite set of values stands for every value: for
numbers and dates, each constant, a point below the lowest, above the highest and between each neighbouring pair;
for text and choices, each constant and one other; for true/false, both; and, for every attribute, no value at all.
`valuations` takes one such value per guarded attribute, so the law proof and Simulate can try every case the kernel
can tell apart. `guard_problems` checks guards against the record class of the data model.

Pure: no IO, no clock, no randomness.
~~~

## Public symbols

* [`MAX_VALUATIONS`](/symbols/domain/value_guards/MAX_VALUATIONS.md) (constant) - no docstring
* [`combinations`](/symbols/domain/value_guards/combinations.md) (function) - `valuations` over these guards, grouped by attribute.
* [`guard_problems`](/symbols/domain/value_guards/guard_problems.md) (function) - Codes for value guards that do not fit the data model's record class: no data model, an attribute the record does not h…
* [`guards_by_attribute`](/symbols/domain/value_guards/guards_by_attribute.md) (function) - Every value guard of the model, grouped by the attribute it reads, attributes in name order.
* [`points`](/symbols/domain/value_guards/points.md) (function) - Values of one attribute that stand for every value its guards can tell apart; None means no value.
* [`valuations`](/symbols/domain/value_guards/valuations.md) (function) - One record's values for each combination of `points` over the guarded attributes, in a fixed order; a value of None is…

## Internal imports

* [`domain/data`](/modules/domain/data.md)
* [`domain/models`](/modules/domain/models.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.data](/modules/domain/data.md) - The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).

## Referenced by

* [application.appgen](/modules/application/appgen.md) - App generation: a reviewed workflow model becomes a runnable app and its conformance oracle (ADR-0150).
* [application.law_proof](/modules/application/law_proof.md) - Prove a pack's laws over every run the kernel allows (ADR-0166).
* [application.simulation](/modules/application/simulation.md) - Seeded simulation of people using the app built from a model (ADR-0152).
* [domain.value_guards.MAX_VALUATIONS](/symbols/domain/value_guards/MAX_VALUATIONS.md) - Constant `MAX_VALUATIONS` in `domain/value_guards`.
* [domain.value_guards.combinations](/symbols/domain/value_guards/combinations.md) - `valuations` over these guards, grouped by attribute.
* [domain.value_guards.guard_problems](/symbols/domain/value_guards/guard_problems.md) - Codes for value guards that do not fit the data model's record class: no data model, an attribute the record does not have, or a constant of another type (or a…
* [domain.value_guards.guards_by_attribute](/symbols/domain/value_guards/guards_by_attribute.md) - Every value guard of the model, grouped by the attribute it reads, attributes in name order.
* [domain.value_guards.points](/symbols/domain/value_guards/points.md) - Values of one attribute that stand for every value its guards can tell apart; None means no value.
* [domain.value_guards.valuations](/symbols/domain/value_guards/valuations.md) - One record's values for each combination of `points` over the guarded attributes, in a fixed order; a value of None is left out.
<!-- okf:generated:end links -->
