---
type: Function
title: application.app_runs.create_cases
description: 'Every fixture actor, and one unknown actor, starting a record with valid values: the state and version it starts in, or the refusal.'
resource: repo://src/eija_studio/application/app_runs.py#create_cases
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/app_runs.py#create_cases
  title: application/app_runs.py
  hash_method: ast-v2
  sha256: 251b503f1d0c40b774a56827f2f9330cc6b5d1f390fdb9b282898550e4420053
notes_baseline: 520ed24fa6deec80b390107e06c710802d9949cb7bc51545b495786e098ff853
---

# application.app_runs.create_cases

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/app_runs`](/modules/application/app_runs.md) |
| Signature | `def create_cases(pack: Pack, model: Workflow) -> list[dict[str, object]]` |
| Code | `repo://src/eija_studio/application/app_runs.py#create_cases` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Every fixture actor, and one unknown actor, starting a record with valid values: the state and version it starts
in, or the refusal. Revoked and unknown actors are refused as the kernel refuses them an action; a model that names
its initiators refuses anyone else (ADR-0231); everyone else gets a record in the model's initial state.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.oracle_session.OracleSession](/symbols/application/oracle_session/OracleSession.md) - In-memory answers to exactly the port calls `execute` makes for one instance.
* [application.oracle_session.UNKNOWN_ACTOR](/symbols/application/oracle_session/UNKNOWN_ACTOR.md) - Constant `UNKNOWN_ACTOR` in `application/oracle_session`.
* [application.oracle_session.absent](/symbols/application/oracle_session/absent.md) - A name guaranteed not to be in `taken`, so a negative case can never collide with a declared one.
* [application.runtime.initialise](/symbols/application/runtime/initialise.md) - Start a record.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
<!-- okf:generated:end links -->
