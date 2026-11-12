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
  sha256: 1f4ad481c7fe20b2620cac42433a4f8fd466651879bc119a1662a28857f91bd0
notes_baseline: f021a414dea4ed4cc8a6baf05fedf92cdc31f90c93d74113bf3464fd8601e2e2
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
* [`move_object`](/symbols/application/oracle_session/OracleSession.move_object.md) - `def move_object(self, instance_id: str, link: str, state: str) -> None`
* [`object_state`](/symbols/application/oracle_session/OracleSession.object_state.md) - `def object_state(self, instance_id: str, link: str) -> str \| None`
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
* [application.appgen.linked_cases](/symbols/application/appgen/linked_cases.md) - For each transition that moves linked objects, an actor who may take it tries it with the objects in every state of their lifecycles, and the kernel's answer,…
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
* [application.oracle_session.OracleSession.move_object](/symbols/application/oracle_session/OracleSession.move_object.md) - `def move_object(self, instance_id: str, link: str, state: str) -> None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.object_state](/symbols/application/oracle_session/OracleSession.object_state.md) - `def object_state(self, instance_id: str, link: str) -> str | None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.record_act](/symbols/application/oracle_session/OracleSession.record_act.md) - `def record_act(self, instance_id: str, action: str, actor_id: str) -> None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.record_operation](/symbols/application/oracle_session/OracleSession.record_operation.md) - `def record_operation(self, operation_id: str, binding: str, result: dict[str, Any]) -> None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.update_instance](/symbols/application/oracle_session/OracleSession.update_instance.md) - `def update_instance(self, item: dict[str, Any], expected: int) -> None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.values](/symbols/application/oracle_session/OracleSession.values.md) - `def values(self, instance_id: str) -> dict[str, Any]` in `application/oracle_session`.
* [application.oracle_session.kernel_answer](/symbols/application/oracle_session/kernel_answer.md) - `def kernel_answer(pack: Pack, model: Workflow, session: OracleSession, actor: str, action: str, version: int,…` in `application/oracle_session`.
<!-- okf:generated:end links -->
