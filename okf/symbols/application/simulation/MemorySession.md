---
type: Class
title: application.simulation.MemorySession
description: The kernel's unit-of-work port over plain dictionaries, keeping every record, operation and effect.
resource: repo://src/eija_studio/application/simulation.py#MemorySession
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/simulation.py#MemorySession
  title: application/simulation.py
  hash_method: ast-sig-v1
  sha256: b9e1986763bf1c3f3d5157696afa7b3c11857b73663d64491444e226a513c50d
notes_baseline: 6d16714a8b99881606e9946f0bbbe210335246bd2b10962fd405c5e8e99a16d9
---

# application.simulation.MemorySession

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/simulation`](/modules/application/simulation.md) |
| Signature | `class MemorySession` |
| Code | `repo://src/eija_studio/application/simulation.py#MemorySession` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
The kernel's unit-of-work port over plain dictionaries, keeping every record, operation and effect.
~~~

## Methods

* [`actor`](/symbols/application/simulation/MemorySession.actor.md) - `def actor(self, actor_id: str) -> dict[str, Any]`
* [`acts`](/symbols/application/simulation/MemorySession.acts.md) - `def acts(self, instance_id: str) -> list[tuple[str, str]]`
* [`create_instance`](/symbols/application/simulation/MemorySession.create_instance.md) - `def create_instance(self, item: dict[str, Any]) -> None`
* [`enqueue`](/symbols/application/simulation/MemorySession.enqueue.md) - `def enqueue(self, case_id: str, operation_id: str, effect: str, recipient: str) -> None`
* [`event`](/symbols/application/simulation/MemorySession.event.md) - `def event(self, kind: str, body: dict[str, Any]) -> None`
* [`find_instance`](/symbols/application/simulation/MemorySession.find_instance.md) - `def find_instance(self, instance_id: str, case_id: str) -> dict[str, Any] \| None`
* [`find_operation`](/symbols/application/simulation/MemorySession.find_operation.md) - `def find_operation(self, operation_id: str) -> dict[str, Any] \| None`
* [`record_act`](/symbols/application/simulation/MemorySession.record_act.md) - `def record_act(self, instance_id: str, action: str, actor_id: str) -> None`
* [`record_operation`](/symbols/application/simulation/MemorySession.record_operation.md) - `def record_operation(self, operation_id: str, binding: str, result: dict[str, Any]) -> None`
* [`update_instance`](/symbols/application/simulation/MemorySession.update_instance.md) - `def update_instance(self, item: dict[str, Any], expected: int) -> None`
* [`values`](/symbols/application/simulation/MemorySession.values.md) - `def values(self, instance_id: str) -> dict[str, Any]`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.simulation.MemorySession.actor](/symbols/application/simulation/MemorySession.actor.md) - `def actor(self, actor_id: str) -> dict[str, Any]` in `application/simulation`.
* [application.simulation.MemorySession.acts](/symbols/application/simulation/MemorySession.acts.md) - `def acts(self, instance_id: str) -> list[tuple[str, str]]` in `application/simulation`.
* [application.simulation.MemorySession.create_instance](/symbols/application/simulation/MemorySession.create_instance.md) - `def create_instance(self, item: dict[str, Any]) -> None` in `application/simulation`.
* [application.simulation.MemorySession.enqueue](/symbols/application/simulation/MemorySession.enqueue.md) - `def enqueue(self, case_id: str, operation_id: str, effect: str, recipient: str) -> None` in `application/simulation`.
* [application.simulation.MemorySession.event](/symbols/application/simulation/MemorySession.event.md) - `def event(self, kind: str, body: dict[str, Any]) -> None` in `application/simulation`.
* [application.simulation.MemorySession.find_instance](/symbols/application/simulation/MemorySession.find_instance.md) - `def find_instance(self, instance_id: str, case_id: str) -> dict[str, Any] | None` in `application/simulation`.
* [application.simulation.MemorySession.find_operation](/symbols/application/simulation/MemorySession.find_operation.md) - `def find_operation(self, operation_id: str) -> dict[str, Any] | None` in `application/simulation`.
* [application.simulation.MemorySession.record_act](/symbols/application/simulation/MemorySession.record_act.md) - `def record_act(self, instance_id: str, action: str, actor_id: str) -> None` in `application/simulation`.
* [application.simulation.MemorySession.record_operation](/symbols/application/simulation/MemorySession.record_operation.md) - `def record_operation(self, operation_id: str, binding: str, result: dict[str, Any]) -> None` in `application/simulation`.
* [application.simulation.MemorySession.update_instance](/symbols/application/simulation/MemorySession.update_instance.md) - `def update_instance(self, item: dict[str, Any], expected: int) -> None` in `application/simulation`.
* [application.simulation.MemorySession.values](/symbols/application/simulation/MemorySession.values.md) - `def values(self, instance_id: str) -> dict[str, Any]` in `application/simulation`.
<!-- okf:generated:end links -->
