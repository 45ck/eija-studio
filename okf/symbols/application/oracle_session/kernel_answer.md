---
type: Function
title: application.oracle_session.kernel_answer
description: '`def kernel_answer(pack: Pack, model: Workflow, session: OracleSession, actor: str, action: str, version: int,…` in `application/oracle_session`.'
resource: repo://src/eija_studio/application/oracle_session.py#kernel_answer
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/oracle_session.py#kernel_answer
  title: application/oracle_session.py
  hash_method: ast-v2
  sha256: 996a6ce74fadd5d4f89da2281c001ac44e999f8f3617204b7b875b2e642524a7
notes_baseline: 030ea28c7b2d532c1ee5700b358247c5b7aad07d493af3a75a360c280cb1023d
---

# application.oracle_session.kernel_answer

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/oracle_session`](/modules/application/oracle_session.md) |
| Signature | `def kernel_answer(pack: Pack, model: Workflow, session: OracleSession, actor: str, action: str, version: int, operation: str='op-1') -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/oracle_session.py#kernel_answer` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.oracle_session.OracleSession](/symbols/application/oracle_session/OracleSession.md) - In-memory answers to exactly the port calls `execute` makes for one instance.
* [application.runtime.execute](/symbols/application/runtime/execute.md) - `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault: Callable[[…` in `application/runtime`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.ExecuteCommand](/symbols/domain/models/ExecuteCommand.md) - `class ExecuteCommand(Contract)` in `domain/models`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.app_runs.options_cases](/symbols/application/app_runs/options_cases.md) - What the app offers each fixture actor (and one unknown actor) on a record in each state that holds valid values: every action leaving that state, and whether…
* [application.appgen.linked_cases](/symbols/application/appgen/linked_cases.md) - For each transition that moves linked objects, an actor who may take it tries it with the objects in every state of their lifecycles, and the kernel's answer,…
* [application.appgen.oracle_cases](/symbols/application/appgen/oracle_cases.md) - Every state x action x actor x expected version, then the same request replayed.
* [application.appgen.separation_cases](/symbols/application/appgen/separation_cases.md) - One fixture actor takes an action of a separation-of-duties law, then tries another the law names, on the same record; the kernel's answer to the second (ADR-0…
* [application.appgen.timer_cases](/symbols/application/appgen/timer_cases.md) - For each transition with a time event, an actor who may take it tries it on a record that has been in the source state half the time and the whole time, and th…
* [application.appgen.value_cases](/symbols/application/appgen/value_cases.md) - For each transition with guards over record values, an actor who may take it tries it on records holding every combination of values its guards can tell apart…
<!-- okf:generated:end links -->
