---
type: Module
title: application.simulation
description: Seeded simulation of people using the app built from a model (ADR-0152).
resource: repo://src/eija_studio/application/simulation.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/simulation.py
  title: application/simulation.py
  hash_method: ast-api-v1
  sha256: 11bb67389e0062fd90bdeabbe189b902f313b8f4fe9c47f4a400011c3fed4d4d
notes_baseline: a5c714d0ffd37e748fa19986c324dadeee4837f108dd46e43df929729d646f24
---

# application.simulation

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/simulation.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Seeded simulation of people using the app built from a model (ADR-0152). Every step is decided by the kernel.

Simulated users are the pack's fixture actors. At each step one of them starts a record or picks one they can work on
and tries an action: usually one their role is offered from the record's state, sometimes any declared action (a slip),
and sometimes with an out-of-date version (someone else got there first). Revoked or unassigned actors still try, as
people do, and the kernel refuses them. `runtime.execute` decides each attempt against an in-memory unit of work, so
the counts, refusal codes and effects are the kernel's own answers, not a second reading of the model. The same seed
gives the same run. Nothing persists and no effect leaves the process. For a model with time events (ADR-0237), each
step lets simulated time pass, so the longest one falls due within a few steps of a record entering its state.
~~~

## Public symbols

* [`CASE`](/symbols/application/simulation/CASE.md) (constant) - no docstring
* [`MAX_BREAKPOINTS`](/symbols/application/simulation/MAX_BREAKPOINTS.md) (constant) - no docstring
* [`MAX_STEPS`](/symbols/application/simulation/MAX_STEPS.md) (constant) - no docstring
* [`MemorySession`](/symbols/application/simulation/MemorySession.md) (class) - The kernel's unit-of-work port over plain dictionaries, keeping every record, operation and effect.
* [`NEW_RECORD`](/symbols/application/simulation/NEW_RECORD.md) (constant) - no docstring
* [`POOL`](/symbols/application/simulation/POOL.md) (constant) - no docstring
* [`SLIP`](/symbols/application/simulation/SLIP.md) (constant) - no docstring
* [`STALE`](/symbols/application/simulation/STALE.md) (constant) - no docstring
* [`TICKS`](/symbols/application/simulation/TICKS.md) (constant) - no docstring
* [`TRACE_LIMIT`](/symbols/application/simulation/TRACE_LIMIT.md) (constant) - no docstring
* [`run_log`](/symbols/application/simulation/run_log.md) (function) - Every step of the seeded run in order, and where a run with these breakpoints stops (ADR-0160).
* [`simulate`](/symbols/application/simulation/simulate.md) (function) - Run `steps` seeded attempts by the pack's fixture actors through the kernel and report where they went.

## Internal imports

* [`application/runtime`](/modules/application/runtime.md)
* [`domain/laws`](/modules/domain/laws.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/value_guards`](/modules/domain/value_guards.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.runtime](/modules/application/runtime.md) - Generic execution algorithm; the domain (policy, laws, typed effects) comes from the pack.
* [domain.laws](/modules/domain/laws.md) - Typed law DSL of a domain pack: what a workflow may never do, stated as data (WBS 1.1/1.2).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.value_guards](/modules/domain/value_guards.md) - Guards over a record's values (issue #93, ADR-0234): which values can decide them, and whether they fit the data model.

## Referenced by

* [application.access](/modules/application/access.md) - Who can do what (ADR-0171): the model's permissions as a role by state matrix, each cell checked by the kernel, and reachability questions such as "can a recor…
* [application.appgen](/modules/application/appgen.md) - App generation: a reviewed workflow model becomes a runnable app and its conformance oracle (ADR-0150).
* [application.law_proof](/modules/application/law_proof.md) - Prove a pack's laws over every run the kernel allows (ADR-0166).
* [application.review](/modules/application/review.md) - Review a model change in PlayIDE instead of a pull request (ADR-0175).
* [application.scenario_run](/modules/application/scenario_run.md) - Run a pack's scenarios (its test cases) through the kernel, and record new ones (ADR-0177).
* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
* [application.simulation.CASE](/symbols/application/simulation/CASE.md) - Constant `CASE` in `application/simulation`.
* [application.simulation.MAX_BREAKPOINTS](/symbols/application/simulation/MAX_BREAKPOINTS.md) - Constant `MAX_BREAKPOINTS` in `application/simulation`.
* [application.simulation.MAX_STEPS](/symbols/application/simulation/MAX_STEPS.md) - Constant `MAX_STEPS` in `application/simulation`.
* [application.simulation.MemorySession.actor](/symbols/application/simulation/MemorySession.actor.md) - `def actor(self, actor_id: str) -> dict[str, Any]` in `application/simulation`.
* [application.simulation.MemorySession.acts](/symbols/application/simulation/MemorySession.acts.md) - `def acts(self, instance_id: str) -> list[tuple[str, str]]` in `application/simulation`.
* [application.simulation.MemorySession.create_instance](/symbols/application/simulation/MemorySession.create_instance.md) - `def create_instance(self, item: dict[str, Any]) -> None` in `application/simulation`.
* [application.simulation.MemorySession.elapsed](/symbols/application/simulation/MemorySession.elapsed.md) - `def elapsed(self, instance_id: str) -> float | None` in `application/simulation`.
* [application.simulation.MemorySession.enqueue](/symbols/application/simulation/MemorySession.enqueue.md) - `def enqueue(self, case_id: str, operation_id: str, effect: str, recipient: str) -> None` in `application/simulation`.
* [application.simulation.MemorySession.event](/symbols/application/simulation/MemorySession.event.md) - `def event(self, kind: str, body: dict[str, Any]) -> None` in `application/simulation`.
* [application.simulation.MemorySession.find_instance](/symbols/application/simulation/MemorySession.find_instance.md) - `def find_instance(self, instance_id: str, case_id: str) -> dict[str, Any] | None` in `application/simulation`.
* [application.simulation.MemorySession.find_operation](/symbols/application/simulation/MemorySession.find_operation.md) - `def find_operation(self, operation_id: str) -> dict[str, Any] | None` in `application/simulation`.
* [application.simulation.MemorySession.link](/symbols/application/simulation/MemorySession.link.md) - Link a record to an object, setting the object's state if given or the object is new (ADR-0241).
* [application.simulation.MemorySession](/symbols/application/simulation/MemorySession.md) - The kernel's unit-of-work port over plain dictionaries, keeping every record, operation and effect.
* [application.simulation.MemorySession.move_object](/symbols/application/simulation/MemorySession.move_object.md) - `def move_object(self, instance_id: str, link: str, state: str) -> None` in `application/simulation`.
* [application.simulation.MemorySession.object_state](/symbols/application/simulation/MemorySession.object_state.md) - `def object_state(self, instance_id: str, link: str) -> str | None` in `application/simulation`.
* [application.simulation.MemorySession.record_act](/symbols/application/simulation/MemorySession.record_act.md) - `def record_act(self, instance_id: str, action: str, actor_id: str) -> None` in `application/simulation`.
* [application.simulation.MemorySession.record_operation](/symbols/application/simulation/MemorySession.record_operation.md) - `def record_operation(self, operation_id: str, binding: str, result: dict[str, Any]) -> None` in `application/simulation`.
* [application.simulation.MemorySession.update_instance](/symbols/application/simulation/MemorySession.update_instance.md) - `def update_instance(self, item: dict[str, Any], expected: int) -> None` in `application/simulation`.
* [application.simulation.MemorySession.values](/symbols/application/simulation/MemorySession.values.md) - `def values(self, instance_id: str) -> dict[str, Any]` in `application/simulation`.
* [application.simulation.MemorySession.wait](/symbols/application/simulation/MemorySession.wait.md) - Let simulated time pass.
* [application.simulation.NEW_RECORD](/symbols/application/simulation/NEW_RECORD.md) - Constant `NEW_RECORD` in `application/simulation`.
* [application.simulation.POOL](/symbols/application/simulation/POOL.md) - Constant `POOL` in `application/simulation`.
* [application.simulation.SLIP](/symbols/application/simulation/SLIP.md) - Constant `SLIP` in `application/simulation`.
* [application.simulation.STALE](/symbols/application/simulation/STALE.md) - Constant `STALE` in `application/simulation`.
* [application.simulation.TICKS](/symbols/application/simulation/TICKS.md) - Constant `TICKS` in `application/simulation`.
* [application.simulation.TRACE_LIMIT](/symbols/application/simulation/TRACE_LIMIT.md) - Constant `TRACE_LIMIT` in `application/simulation`.
* [application.simulation.run_log](/symbols/application/simulation/run_log.md) - Every step of the seeded run in order, and where a run with these breakpoints stops (ADR-0160).
* [application.simulation.simulate](/symbols/application/simulation/simulate.md) - Run `steps` seeded attempts by the pack's fixture actors through the kernel and report where they went.
<!-- okf:generated:end links -->
