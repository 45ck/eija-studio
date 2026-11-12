---
type: Module
title: application.oracle_session
description: 'The in-memory session the app oracle asks the kernel through (ADR-0150): one record, nothing persists.'
resource: repo://src/eija_studio/application/oracle_session.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/oracle_session.py
  title: application/oracle_session.py
  hash_method: ast-api-v1
  sha256: b486f22e1e9ad346e07201de6d715333aedfd6e3da16fa0ded7ca813385bf80c
notes_baseline: 8d62e790f32f09f62569f66df9844c61f3e04f68ebb927af683a6e8ddde45321
---

# application.oracle_session

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/oracle_session.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
The in-memory session the app oracle asks the kernel through (ADR-0150): one record, nothing persists.
~~~

## Public symbols

* [`OracleSession`](/symbols/application/oracle_session/OracleSession.md) (class) - In-memory answers to exactly the port calls `execute` makes for one instance.
* [`UNKNOWN_ACTOR`](/symbols/application/oracle_session/UNKNOWN_ACTOR.md) (constant) - no docstring
* [`absent`](/symbols/application/oracle_session/absent.md) (function) - A name guaranteed not to be in `taken`, so a negative case can never collide with a declared one.
* [`kernel_answer`](/symbols/application/oracle_session/kernel_answer.md) (function) - no docstring

## Internal imports

* [`application/memo`](/modules/application/memo.md)
* [`application/runtime`](/modules/application/runtime.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.memo](/modules/application/memo.md) - Ask the kernel the same question of the same frozen model once (ADR-0199).
* [application.runtime](/modules/application/runtime.md) - Generic execution algorithm; the domain (policy, laws, typed effects) comes from the pack.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [application.app_runs](/modules/application/app_runs.md) - The app oracle's runs that start from a record the app itself creates (ADR-0241): who may start one and where it starts, a run from a new record to each transi…
* [application.appgen](/modules/application/appgen.md) - App generation: a reviewed workflow model becomes a runnable app and its conformance oracle (ADR-0150).
* [application.oracle_session.OracleSession.actor](/symbols/application/oracle_session/OracleSession.actor.md) - `def actor(self, actor_id: str) -> dict[str, Any]` in `application/oracle_session`.
* [application.oracle_session.OracleSession.acts](/symbols/application/oracle_session/OracleSession.acts.md) - `def acts(self, instance_id: str) -> list[tuple[str, str]]` in `application/oracle_session`.
* [application.oracle_session.OracleSession.create_instance](/symbols/application/oracle_session/OracleSession.create_instance.md) - `def create_instance(self, item: dict[str, Any]) -> None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.elapsed](/symbols/application/oracle_session/OracleSession.elapsed.md) - `def elapsed(self, instance_id: str) -> float | None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.enqueue](/symbols/application/oracle_session/OracleSession.enqueue.md) - `def enqueue(self, case_id: str, operation_id: str, effect: str, recipient: str) -> None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.event](/symbols/application/oracle_session/OracleSession.event.md) - `def event(self, kind: str, body: dict[str, Any]) -> None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.find_instance](/symbols/application/oracle_session/OracleSession.find_instance.md) - `def find_instance(self, instance_id: str, case_id: str) -> dict[str, Any] | None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.find_operation](/symbols/application/oracle_session/OracleSession.find_operation.md) - `def find_operation(self, operation_id: str) -> dict[str, Any] | None` in `application/oracle_session`.
* [application.oracle_session.OracleSession](/symbols/application/oracle_session/OracleSession.md) - In-memory answers to exactly the port calls `execute` makes for one instance.
* [application.oracle_session.OracleSession.record_act](/symbols/application/oracle_session/OracleSession.record_act.md) - `def record_act(self, instance_id: str, action: str, actor_id: str) -> None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.record_operation](/symbols/application/oracle_session/OracleSession.record_operation.md) - `def record_operation(self, operation_id: str, binding: str, result: dict[str, Any]) -> None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.update_instance](/symbols/application/oracle_session/OracleSession.update_instance.md) - `def update_instance(self, item: dict[str, Any], expected: int) -> None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.values](/symbols/application/oracle_session/OracleSession.values.md) - `def values(self, instance_id: str) -> dict[str, Any]` in `application/oracle_session`.
* [application.oracle_session.UNKNOWN_ACTOR](/symbols/application/oracle_session/UNKNOWN_ACTOR.md) - Constant `UNKNOWN_ACTOR` in `application/oracle_session`.
* [application.oracle_session.absent](/symbols/application/oracle_session/absent.md) - A name guaranteed not to be in `taken`, so a negative case can never collide with a declared one.
* [application.oracle_session.kernel_answer](/symbols/application/oracle_session/kernel_answer.md) - `def kernel_answer(pack: Pack, model: Workflow, session: OracleSession, actor: str, action: str, version: int,…` in `application/oracle_session`.
<!-- okf:generated:end links -->
