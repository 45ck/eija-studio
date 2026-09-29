---
type: Class
title: application.ports.UnitOfWork
description: 'The application-owned persistence port: all mutations on it commit together or roll back together.'
resource: repo://src/eija_studio/application/ports.py#UnitOfWork
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/ports.py#UnitOfWork
  title: application/ports.py
  hash_method: ast-sig-v1
  sha256: 31ef011814b1d1e414590677a0bca832e8aa0440a533c8ab3fac960464208afa
description_override: 'The application-owned persistence port: all mutations on it commit together or roll back together.'
notes_baseline: fd3a5271fb735e4f9da1c9f2edf1ed4d4837ea81814f7678a8505d6a8b8dc10b
---

# application.ports.UnitOfWork

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/ports`](/modules/application/ports.md) |
| Signature | `class UnitOfWork(Protocol)` |
| Code | `repo://src/eija_studio/application/ports.py#UnitOfWork` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
All mutations on this port commit together or roll back together.
~~~

## Protocol members

Structural interface implemented by adapters; not a class to instantiate.

* `def load_case(self, case_id: str) -> dict[str, Any]`
* `def save_case(self, case: dict[str, Any], expected: int) -> None`
* `def insert_case(self, case: dict[str, Any]) -> None`
* `def active(self) -> dict[str, Any]`
* `def set_active(self, model: Workflow, expected: int) -> None`
* `def event(self, kind: str, body: dict[str, Any]) -> None`
* `def actor(self, actor_id: str) -> dict[str, Any]`
* `def create_instance(self, item: dict[str, Any]) -> None`
* `def find_instance(self, instance_id: str, case_id: str) -> dict[str, Any] \| None`
* `def update_instance(self, item: dict[str, Any], expected: int) -> None`
* `def find_operation(self, operation_id: str) -> dict[str, Any] \| None`
* `def record_operation(self, operation_id: str, binding: str, result: dict[str, Any]) -> None`
* `def enqueue(self, case_id: str, operation_id: str, effect: str) -> None`
* `def observations(self, case_id: str) -> dict[str, Any]`
* `def effect_counts(self) -> dict[str, Any]`
<!-- okf:generated:end facts -->

## Notes

Adapters implement it structurally ([SQLite store](/modules/adapters/sqlite_store.md)); domain and application never import SQL types. A new backend must reproduce compare-and-swap, replay and atomicity before use.

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [Execution](/contexts/execution.md) - Owns Trusted fixture actor state, preview instances, command replay, committed effect intents
* [application.ports.Repository](/symbols/application/ports/Repository.md) - `class Repository(Protocol)` in `application/ports`.
* [application.runtime.execute](/symbols/application/runtime/execute.md) - `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault: Callable[[…` in `application/runtime`.
* [application.runtime.initialise](/symbols/application/runtime/initialise.md) - `def initialise(session: UnitOfWork, case_id: str, model: Workflow, *, state: str | None=None) -> dict[str, An…` in `application/runtime`.
<!-- okf:generated:end links -->
