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
  sha256: b3b7128768ba15d153c3eb945d02dfa31c8d6bff882364cb2691e670d8e5c945
notes_baseline: 3ef559e5507ef9d783ee87093b32d754c0532d8b29c892a0192b93114b265210
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
* [`data_cases`](/symbols/application/appgen/data_cases.md) (function) - Record values to create with, and `check_values`' answer for each: a valid record, then each required value missing, ea…
* [`generate`](/symbols/application/appgen/generate.md) (function) - Return the per-model files and the build manifest (without file hashes or test results).
* [`oracle_cases`](/symbols/application/appgen/oracle_cases.md) (function) - Every state x action x actor x expected version, then the same request replayed.
* [`readme`](/symbols/application/appgen/readme.md) (function) - no docstring

## Internal imports

* [`application/memo`](/modules/application/memo.md)
* [`application/runtime`](/modules/application/runtime.md)
* [`domain/data`](/modules/domain/data.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/policy`](/modules/domain/policy.md)
* [`domain/screens`](/modules/domain/screens.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.memo](/modules/application/memo.md) - Ask the kernel the same question of the same frozen model once (ADR-0199).
* [application.runtime](/modules/application/runtime.md) - Generic execution algorithm; the domain (policy, laws, typed effects) comes from the pack.
* [domain.data](/modules/domain/data.md) - The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.policy](/modules/domain/policy.md) - Generic policy: coherence with a domain pack's declared action catalog, the pack's laws, and declared effects.
* [domain.screens](/modules/domain/screens.md) - Screens: the user interface of a pack's app, designed against its use cases and data model (ADR-0154).

## Referenced by

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
* [application.appgen.data_cases](/symbols/application/appgen/data_cases.md) - Record values to create with, and `check_values`' answer for each: a valid record, then each required value missing, each value of the wrong type, each text on…
* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
* [application.appgen.oracle_cases](/symbols/application/appgen/oracle_cases.md) - Every state x action x actor x expected version, then the same request replayed.
* [application.appgen.readme](/symbols/application/appgen/readme.md) - `def readme(pack: Pack, model: Workflow, cases: int, data: DataModel | None=None) -> str` in `application/appgen`.
<!-- okf:generated:end links -->
