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
  sha256: a86ccebf6eecd7887c9c30b15390d170333d717e59d48d4d7803c5307dbbe742
description_override: 'The application-owned persistence port: all mutations on it commit together or roll back together.'
notes_baseline: 9e90e724fcd0e2e22ef7231c62111723241f7db412f01297cc7aac4d952d6b5c
verified:
- by: process:claude-code-integration-phase0
  at: '2026-09-29T04:30:00Z'
  notes_sha256: 1bac22a1ccff4b30399a3a52a6ab9d82261992b125aa55337fe6cc7ec9447139
  sources_sha256: 1545ec9c17df092b8f153cb805f59c2582f86c8bc012c4bb81cecb62a7e230cf
- by: process:eija-wbs-1.3-agent
  at: '2026-09-29T08:20:47Z'
  notes_sha256: 1bac22a1ccff4b30399a3a52a6ab9d82261992b125aa55337fe6cc7ec9447139
  sources_sha256: 35eaf8f9d8740a3c9cdad00d2333de026fd86e5245a526cd7f1c957ddd5ea7e7
- by: process:playide-exact-app
  at: '2026-10-11T09:17:31Z'
  notes_sha256: 52922a912ec79fcbcb0554a013b8665ac986cb84331ccd029c30e8e276da4584
  sources_sha256: 06e26f3221c1b55b1031bedb6a369e24872a980943d6c8e60786facbe105acb1
- by: process:claude-code
  at: '2026-11-11T12:00:00Z'
  notes_sha256: 7dce7165a960defbf5f33e17489096c47278d515079a5030eae412de1b68fda2
  sources_sha256: 9d33ae79e381cad30bf3f71954ffd7e15f429d0b56771bfb09dee2efd3f0c044
- by: process:claude-code
  at: '2026-11-11T22:00:00Z'
  notes_sha256: 448e0930c163b9e7b8b61199016d9f35b3d2436c1c7a60e00aa492933efb0d1f
  sources_sha256: 42cb670ad72a95d4e3c114fbb80a2a0407ad9b4268d20a4e4d8992cf2f83fa95
- by: process:claude-code
  at: '2026-11-12T03:00:00Z'
  notes_sha256: b1b4962665107c932cf5e618b0ff32e900b4403e9e68d1034359d1ad16517d45
  sources_sha256: ff2b9471c12f8f4ac45f48d285a9a9c03a1f742d82c82452e8fefbc74de9da9a
- by: process:claude-code
  at: '2026-11-12T04:00:08Z'
  notes_sha256: 3782b99a4129bf5e20f249ec2d393ce9c9c0e931dcecb065b29226041cc467ff
  sources_sha256: 9e90e724fcd0e2e22ef7231c62111723241f7db412f01297cc7aac4d952d6b5c
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
* `def set_active(self, model: Workflow, expected: int, app_build: dict[str, Any] \| None=None) -> None`
* `def event(self, kind: str, body: dict[str, Any]) -> None`
* `def actor(self, actor_id: str) -> dict[str, Any]`
* `def create_instance(self, item: dict[str, Any]) -> None`
* `def find_instance(self, instance_id: str, case_id: str) -> dict[str, Any] \| None`
* `def update_instance(self, item: dict[str, Any], expected: int) -> None`
* `def acts(self, instance_id: str) -> list[tuple[str, str]]`
* `def record_act(self, instance_id: str, action: str, actor_id: str) -> None`
* `def values(self, instance_id: str) -> dict[str, Any]`
* `def elapsed(self, instance_id: str) -> float \| None`
* `def object_state(self, instance_id: str, link: str) -> str \| None`
* `def move_object(self, instance_id: str, link: str, state: str) -> None`
* `def find_operation(self, operation_id: str) -> dict[str, Any] \| None`
* `def record_operation(self, operation_id: str, binding: str, result: dict[str, Any]) -> None`
* `def enqueue(self, case_id: str, operation_id: str, effect: str, recipient: str) -> None`
* `def observations(self, case_id: str) -> dict[str, Any]`
* `def effect_counts(self) -> dict[str, Any]`
<!-- okf:generated:end facts -->

## Notes

Adapters implement it structurally ([SQLite store](/modules/adapters/sqlite_store.md)); domain and application never import SQL types. A new backend must reproduce compare-and-swap, replay and atomicity before use.

`values` returns a record's values for a transition with guards over them (ADR-0234); a store without record values returns `{}`, so such guards fail closed. `elapsed` returns how many seconds the record has been in its current state, by the adapter's clock, read only for a transition with a time event ([ADR-0237](/adrs/0237-time-events.md)); a store that keeps no clock returns None, which is never due. `acts` and `record_act` keep who took which action on a record, read and written only for actions a separation-of-duties law names ([ADR-0233](/adrs/0233-separation-of-duties.md)). `object_state` and `move_object` read and write the state of the object a record links to, only for a transition that moves one ([ADR-0241](/adrs/0241-actions-on-linked-objects.md)); a store that keeps no objects returns None, which refuses the step.

set_active also accepts the optional generated-app association. Adapters commit the new baseline, association and applied case together; a workflow-only activation clears an earlier exact-app association rather than borrowing it.

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [Execution](/contexts/execution.md) - Owns Trusted fixture actor state, preview instances, command replay, committed effect intents
* [application.ports.Repository](/symbols/application/ports/Repository.md) - `class Repository(Protocol)` in `application/ports`.
* [application.runtime.check_starter](/symbols/application/runtime/check_starter.md) - The role of the actor starting a record: an unknown actor is refused by the directory and a revoked one as it is refused an action (ADR-0250), so whoever start…
* [application.runtime.execute](/symbols/application/runtime/execute.md) - `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault: Callable[[…` in `application/runtime`.
* [application.runtime.initialise](/symbols/application/runtime/initialise.md) - Start a record.
* [application.runtime.receive](/symbols/application/runtime/receive.md) - Start a record because another workflow of the system sent `signal` (issue #93 item 5, ADR-0242).
<!-- okf:generated:end links -->
