---
type: Function
title: application.app_runs.options_cases
description: 'What the app offers each fixture actor (and one unknown actor) on a record in each state that holds valid values: every action leaving that state, and whether the kernel would take it from there at version 0, with its r…'
resource: repo://src/eija_studio/application/app_runs.py#options_cases
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/app_runs.py#options_cases
  title: application/app_runs.py
  hash_method: ast-v2
  sha256: bd30118bc8759736681a0fc9805ac44aaca5a1c9ae4a74078d127a7b95de4c7c
notes_baseline: 8a2d17cd186251b8e7db67f6b1344d6582cfbab4506686f215931b3b278f590f
---

# application.app_runs.options_cases

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/app_runs`](/modules/application/app_runs.md) |
| Signature | `def options_cases(pack: Pack, model: Workflow, valid: dict[str, Any]) -> list[dict[str, Any]]` |
| Code | `repo://src/eija_studio/application/app_runs.py#options_cases` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
What the app offers each fixture actor (and one unknown actor) on a record in each state that holds valid
values: every action leaving that state, and whether the kernel would take it from there at version 0, with its
refusal code when it would not.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.oracle_session.OracleSession](/symbols/application/oracle_session/OracleSession.md) - In-memory answers to exactly the port calls `execute` makes for one instance.
* [application.oracle_session.UNKNOWN_ACTOR](/symbols/application/oracle_session/UNKNOWN_ACTOR.md) - Constant `UNKNOWN_ACTOR` in `application/oracle_session`.
* [application.oracle_session.absent](/symbols/application/oracle_session/absent.md) - A name guaranteed not to be in `taken`, so a negative case can never collide with a declared one.
* [application.oracle_session.kernel_answer](/symbols/application/oracle_session/kernel_answer.md) - `def kernel_answer(pack: Pack, model: Workflow, session: OracleSession, actor: str, action: str, version: int,…` in `application/oracle_session`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
<!-- okf:generated:end links -->
