---
type: Module
title: application.appgen
description: 'App generation: a reviewed workflow model becomes a runnable app and its conformance oracle (ADR-0150).'
resource: repo://src/eija_studio/application/appgen.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/appgen.py
  title: application/appgen.py
  hash_method: ast-api-v1
  sha256: 113b099c0b9252489ce1eba57b26bdc71d004efdc7b0e1be558881eebe552dad
notes_baseline: 5fe2a8571b063dc7cb09a5d6e65f0d9ed9e067dc1ae790ae6ea116d516a7a993
---

# application.appgen

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/appgen.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
App generation: a reviewed workflow model becomes a runnable app and its conformance oracle (ADR-0150).

The generated app is storage, HTTP and a page from fixed templates (`resources/appgen/`). It has no rules of its own: it
calls the kernel's `runtime.execute` and `runtime.initialise` through a SQLite unit of work, on the `app/model.json` and
`app/pack.json` written here. `tests/oracle.json` holds the kernel's answer for every case on an in-memory session, so
the app passes only if its storage, transactions and effects keep the kernel's behaviour end to end.

Pure: no IO, no clock, no randomness. The same pack and model always give byte-identical files.
~~~

## Public symbols

* [`FORMAT`](/symbols/application/appgen/FORMAT.md) (constant) - no docstring
* [`LIMITS`](/symbols/application/appgen/LIMITS.md) (constant) - no docstring
* [`NO_DATA`](/symbols/application/appgen/NO_DATA.md) (constant) - no docstring
* [`SAMPLES`](/symbols/application/appgen/SAMPLES.md) (constant) - no docstring
* [`UNDECLARED_ACTION`](/symbols/application/appgen/UNDECLARED_ACTION.md) (constant) - no docstring
* [`UNKNOWN_ACTOR`](/symbols/application/appgen/UNKNOWN_ACTOR.md) (constant) - no docstring
* [`WITH_DATA`](/symbols/application/appgen/WITH_DATA.md) (constant) - no docstring
* [`WRONG`](/symbols/application/appgen/WRONG.md) (constant) - no docstring
* [`absent`](/symbols/application/appgen/absent.md) (function) - A name guaranteed not to be in `taken`, so a negative case can never collide with a declared one.
* [`app_limits`](/symbols/application/appgen/app_limits.md) (function) - no docstring
* [`data_cases`](/symbols/application/appgen/data_cases.md) (function) - Record values to create with, and `check_record`'s answer for each: a valid record, then each required value missing, e…
* [`generate`](/symbols/application/appgen/generate.md) (function) - Return the per-model files and the build manifest (without file hashes or test results).
* [`may_start`](/symbols/application/appgen/may_start.md) (function) - Whether the model lets this role start a record (ADR-0231): any role when it names no initiators.
* [`oracle_cases`](/symbols/application/appgen/oracle_cases.md) (function) - Every state x action x actor x expected version, then the same request replayed.
* [`readme`](/symbols/application/appgen/readme.md) (function) - no docstring
* [`separation_cases`](/symbols/application/appgen/separation_cases.md) (function) - One fixture actor takes an action of a separation-of-duties law, then tries another the law names, on the same record;…
* [`start_cases`](/symbols/application/appgen/start_cases.md) (function) - Each active fixture actor starting a record, and the kernel's answer.
* [`stock`](/symbols/application/appgen/stock.md) (function) - One valid object of each class a record refers to (ADR-0235), stored before the data cases run.
* [`value_cases`](/symbols/application/appgen/value_cases.md) (function) - For each transition with guards over record values, an actor who may take it tries it on records holding every combinat…

## Internal imports

* [`application/memo`](/modules/application/memo.md)
* [`application/runtime`](/modules/application/runtime.md)
* [`domain/data`](/modules/domain/data.md)
* [`domain/laws`](/modules/domain/laws.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/navigation`](/modules/domain/navigation.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/policy`](/modules/domain/policy.md)
* [`domain/screens`](/modules/domain/screens.md)
* [`domain/value_guards`](/modules/domain/value_guards.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.memo](/modules/application/memo.md) - Ask the kernel the same question of the same frozen model once (ADR-0199).
* [application.runtime](/modules/application/runtime.md) - Generic execution algorithm; the domain (policy, laws, typed effects) comes from the pack.
* [domain.data](/modules/domain/data.md) - The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.
* [domain.laws](/modules/domain/laws.md) - Typed law DSL of a domain pack: what a workflow may never do, stated as data (WBS 1.1/1.2).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.navigation](/modules/domain/navigation.md) - The generated app's bounded navigation, derived from its existing contracts.
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.policy](/modules/domain/policy.md) - Generic policy: coherence with a domain pack's declared action catalog, the pack's laws, and declared effects.
* [domain.screens](/modules/domain/screens.md) - Screens: the user interface of a pack's app, designed against its use cases and data model (ADR-0154).
* [domain.value_guards](/modules/domain/value_guards.md) - Guards over a record's values (issue #93, ADR-0234): which values can decide them, and whether they fit the data model.

## Referenced by

* [application.generated_app](/modules/application/generated_app.md) - Shared generation and exact-app evidence operations for the existing kernel and checker.
* [interfaces.app_build](/modules/interfaces/app_build.md) - `eija build`: write a runnable app generated from a pack's model, then run its kernel conformance tests (ADR-0150).
* [application.appgen.FORMAT](/symbols/application/appgen/FORMAT.md) - Constant `FORMAT` in `application/appgen`.
* [application.appgen.LIMITS](/symbols/application/appgen/LIMITS.md) - Constant `LIMITS` in `application/appgen`.
* [application.appgen.NO_DATA](/symbols/application/appgen/NO_DATA.md) - Constant `NO_DATA` in `application/appgen`.
* [application.appgen.SAMPLES](/symbols/application/appgen/SAMPLES.md) - Constant `SAMPLES` in `application/appgen`.
* [application.appgen.UNDECLARED_ACTION](/symbols/application/appgen/UNDECLARED_ACTION.md) - Constant `UNDECLARED_ACTION` in `application/appgen`.
* [application.appgen.UNKNOWN_ACTOR](/symbols/application/appgen/UNKNOWN_ACTOR.md) - Constant `UNKNOWN_ACTOR` in `application/appgen`.
* [application.appgen.WITH_DATA](/symbols/application/appgen/WITH_DATA.md) - Constant `WITH_DATA` in `application/appgen`.
* [application.appgen.WRONG](/symbols/application/appgen/WRONG.md) - Constant `WRONG` in `application/appgen`.
* [application.appgen.absent](/symbols/application/appgen/absent.md) - A name guaranteed not to be in `taken`, so a negative case can never collide with a declared one.
* [application.appgen.app_limits](/symbols/application/appgen/app_limits.md) - `def app_limits(data: DataModel | None) -> list[str]` in `application/appgen`.
* [application.appgen.data_cases](/symbols/application/appgen/data_cases.md) - Record values to create with, and `check_record`'s answer for each: a valid record, then each required value missing, each value of the wrong type, each text o…
* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
* [application.appgen.may_start](/symbols/application/appgen/may_start.md) - Whether the model lets this role start a record (ADR-0231): any role when it names no initiators.
* [application.appgen.oracle_cases](/symbols/application/appgen/oracle_cases.md) - Every state x action x actor x expected version, then the same request replayed.
* [application.appgen.readme](/symbols/application/appgen/readme.md) - `def readme(pack: Pack, model: Workflow, cases: int, data: DataModel | None=None) -> str` in `application/appgen`.
* [application.appgen.separation_cases](/symbols/application/appgen/separation_cases.md) - One fixture actor takes an action of a separation-of-duties law, then tries another the law names, on the same record; the kernel's answer to the second (ADR-0…
* [application.appgen.start_cases](/symbols/application/appgen/start_cases.md) - Each active fixture actor starting a record, and the kernel's answer.
* [application.appgen.stock](/symbols/application/appgen/stock.md) - One valid object of each class a record refers to (ADR-0235), stored before the data cases run.
* [application.appgen.value_cases](/symbols/application/appgen/value_cases.md) - For each transition with guards over record values, an actor who may take it tries it on records holding every combination of values its guards can tell apart…
<!-- okf:generated:end links -->
