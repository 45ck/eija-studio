---
type: Module
title: application.appgen
description: 'App generation: a reviewed workflow model becomes the spec and the conformance oracle of a runnable app (ADR-0150).'
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
  sha256: 9ee28884d029b7516f3dd33377a3458e5bb0a76961dc236d0add45faf62bf492
notes_baseline: e2a437196729e8ec6a260fb54cebc237e2646f7ef0b4d42a04efc3972626c910
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
App generation: a reviewed workflow model becomes the spec and the conformance oracle of a runnable app (ADR-0150).

The generated app's runtime is a fixed template (`resources/appgen/`); what changes per model is `app/spec.py`, written
here as plain Python literals that read like the diagram, and `tests/oracle.json`. The oracle is not this module's
reading of the model: every case is answered by the kernel's own `runtime.execute` against an in-memory session, so the
generated app passes its tests only if it refuses and commits exactly where the kernel does.

Pure: no IO, no clock, no randomness. The same pack and model always give byte-identical files.
~~~

## Public symbols

* [`FORMAT`](/symbols/application/appgen/FORMAT.md) (constant) - no docstring
* [`LIMITS`](/symbols/application/appgen/LIMITS.md) (constant) - no docstring
* [`UNDECLARED_ACTION`](/symbols/application/appgen/UNDECLARED_ACTION.md) (constant) - no docstring
* [`UNKNOWN_ACTOR`](/symbols/application/appgen/UNKNOWN_ACTOR.md) (constant) - no docstring
* [`generate`](/symbols/application/appgen/generate.md) (function) - Return the per-model files and the build manifest (without file hashes or test results).
* [`oracle_cases`](/symbols/application/appgen/oracle_cases.md) (function) - Every state x action x actor x expected version, then the same request replayed.
* [`readme`](/symbols/application/appgen/readme.md) (function) - no docstring
* [`spec_source`](/symbols/application/appgen/spec_source.md) (function) - no docstring

## Internal imports

* [`application/runtime`](/modules/application/runtime.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/policy`](/modules/domain/policy.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.runtime](/modules/application/runtime.md) - Generic execution algorithm; the domain (policy, laws, typed effects) comes from the pack.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.policy](/modules/domain/policy.md) - Generic policy: coherence with a domain pack's declared action catalog, the pack's laws, and declared effects.

## Referenced by

* [interfaces.app_build](/modules/interfaces/app_build.md) - `eija build`: write a runnable app generated from a pack's model, then run its kernel conformance tests (ADR-0150).
* [application.appgen.FORMAT](/symbols/application/appgen/FORMAT.md) - Constant `FORMAT` in `application/appgen`.
* [application.appgen.LIMITS](/symbols/application/appgen/LIMITS.md) - Constant `LIMITS` in `application/appgen`.
* [application.appgen.UNDECLARED_ACTION](/symbols/application/appgen/UNDECLARED_ACTION.md) - Constant `UNDECLARED_ACTION` in `application/appgen`.
* [application.appgen.UNKNOWN_ACTOR](/symbols/application/appgen/UNKNOWN_ACTOR.md) - Constant `UNKNOWN_ACTOR` in `application/appgen`.
* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
* [application.appgen.oracle_cases](/symbols/application/appgen/oracle_cases.md) - Every state x action x actor x expected version, then the same request replayed.
* [application.appgen.readme](/symbols/application/appgen/readme.md) - `def readme(pack: Pack, model: Workflow, cases: int) -> str` in `application/appgen`.
* [application.appgen.spec_source](/symbols/application/appgen/spec_source.md) - `def spec_source(pack: Pack, model: Workflow) -> str` in `application/appgen`.
<!-- okf:generated:end links -->
