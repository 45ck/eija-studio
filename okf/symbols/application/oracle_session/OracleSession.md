---
type: Class
title: application.oracle_session.OracleSession
description: In-memory answers to exactly the port calls `execute` makes for one instance.
resource: repo://src/eija_studio/application/oracle_session.py#OracleSession
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/oracle_session.py#OracleSession
  title: application/oracle_session.py
  hash_method: ast-sig-v1
  sha256: 184eafa6f35c9aaa1fe11a2477243c4e0ddd38a3727dda77fbfc296a44544a20
notes_baseline: 5c7e142784c7b3ff8d379abb2b7be247f990e25f70632d8d51b7dc6bebaf4ca7
---

# application.oracle_session.OracleSession

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/oracle_session`](/modules/application/oracle_session.md) |
| Signature | `class OracleSession` |
| Code | `repo://src/eija_studio/application/oracle_session.py#OracleSession` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
In-memory answers to exactly the port calls `execute` makes for one instance. Nothing persists.
~~~

## Methods

* [`actor`](/symbols/application/oracle_session/OracleSession.actor.md) - `def actor(self, actor_id: str) -> dict[str, Any]`
* [`acts`](/symbols/application/oracle_session/OracleSession.acts.md) - `def acts(self, instance_id: str) -> list[tuple[str, str]]`
* [`create_instance`](/symbols/application/oracle_session/OracleSession.create_instance.md) - `def create_instance(self, item: dict[str, Any]) -> None`
* [`elapsed`](/symbols/application/oracle_session/OracleSession.elapsed.md) - `def elapsed(self, instance_id: str) -> float \| None`
* [`enqueue`](/symbols/application/oracle_session/OracleSession.enqueue.md) - `def enqueue(self, case_id: str, operation_id: str, effect: str, recipient: str) -> None`
* [`event`](/symbols/application/oracle_session/OracleSession.event.md) - `def event(self, kind: str, body: dict[str, Any]) -> None`
* [`find_instance`](/symbols/application/oracle_session/OracleSession.find_instance.md) - `def find_instance(self, instance_id: str, case_id: str) -> dict[str, Any] \| None`
* [`find_operation`](/symbols/application/oracle_session/OracleSession.find_operation.md) - `def find_operation(self, operation_id: str) -> dict[str, Any] \| None`
* [`record_act`](/symbols/application/oracle_session/OracleSession.record_act.md) - `def record_act(self, instance_id: str, action: str, actor_id: str) -> None`
* [`record_operation`](/symbols/application/oracle_session/OracleSession.record_operation.md) - `def record_operation(self, operation_id: str, binding: str, result: dict[str, Any]) -> None`
* [`update_instance`](/symbols/application/oracle_session/OracleSession.update_instance.md) - `def update_instance(self, item: dict[str, Any], expected: int) -> None`
* [`values`](/symbols/application/oracle_session/OracleSession.values.md) - `def values(self, instance_id: str) -> dict[str, Any]`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.app_runs.create_cases](/symbols/application/app_runs/create_cases.md) - Every fixture actor, and one unknown actor, starting a record with valid values: the state and version it starts in, or the refusal.
* [application.app_runs.options_cases](/symbols/application/app_runs/options_cases.md) - What the app offers each fixture actor (and one unknown actor) on a record in each state that holds valid values: every action leaving that state, and whether…
* [application.appgen.oracle_cases](/symbols/application/appgen/oracle_cases.md) - Every state x action x actor x expected version, then the same request replayed.
* [application.appgen.separation_cases](/symbols/application/appgen/separation_cases.md) - One fixture actor takes an action of a separation-of-duties law, then tries another the law names, on the same record; the kernel's answer to the second (ADR-0…
* [application.appgen.timer_cases](/symbols/application/appgen/timer_cases.md) - For each transition with a time event, an actor who may take it tries it on a record that has been in the source state half the time and the whole time, and th…
* [application.appgen.value_cases](/symbols/application/appgen/value_cases.md) - For each transition with guards over record values, an actor who may take it tries it on records holding every combination of values its guards can tell apart…
* [application.oracle_session.OracleSession.actor](/symbols/application/oracle_session/OracleSession.actor.md) - `def actor(self, actor_id: str) -> dict[str, Any]` in `application/oracle_session`.
* [application.oracle_session.OracleSession.acts](/symbols/application/oracle_session/OracleSession.acts.md) - `def acts(self, instance_id: str) -> list[tuple[str, str]]` in `application/oracle_session`.
* [application.oracle_session.OracleSession.create_instance](/symbols/application/oracle_session/OracleSession.create_instance.md) - `def create_instance(self, item: dict[str, Any]) -> None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.elapsed](/symbols/application/oracle_session/OracleSession.elapsed.md) - `def elapsed(self, instance_id: str) -> float | None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.enqueue](/symbols/application/oracle_session/OracleSession.enqueue.md) - `def enqueue(self, case_id: str, operation_id: str, effect: str, recipient: str) -> None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.event](/symbols/application/oracle_session/OracleSession.event.md) - `def event(self, kind: str, body: dict[str, Any]) -> None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.find_instance](/symbols/application/oracle_session/OracleSession.find_instance.md) - `def find_instance(self, instance_id: str, case_id: str) -> dict[str, Any] | None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.find_operation](/symbols/application/oracle_session/OracleSession.find_operation.md) - `def find_operation(self, operation_id: str) -> dict[str, Any] | None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.record_act](/symbols/application/oracle_session/OracleSession.record_act.md) - `def record_act(self, instance_id: str, action: str, actor_id: str) -> None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.record_operation](/symbols/application/oracle_session/OracleSession.record_operation.md) - `def record_operation(self, operation_id: str, binding: str, result: dict[str, Any]) -> None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.update_instance](/symbols/application/oracle_session/OracleSession.update_instance.md) - `def update_instance(self, item: dict[str, Any], expected: int) -> None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.values](/symbols/application/oracle_session/OracleSession.values.md) - `def values(self, instance_id: str) -> dict[str, Any]` in `application/oracle_session`.
* [application.oracle_session.kernel_answer](/symbols/application/oracle_session/kernel_answer.md) - `def kernel_answer(pack: Pack, model: Workflow, session: OracleSession, actor: str, action: str, version: int,…` in `application/oracle_session`.
<!-- okf:generated:end links -->
