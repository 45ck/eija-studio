# Symbols of application.simulation

# Classes

* [application.simulation.MemorySession](MemorySession.md) - The kernel's unit-of-work port over plain dictionaries, keeping every record, operation and effect.

# Constants

* [application.simulation.CASE](CASE.md) - Constant `CASE` in `application/simulation`.
* [application.simulation.MAX_BREAKPOINTS](MAX_BREAKPOINTS.md) - Constant `MAX_BREAKPOINTS` in `application/simulation`.
* [application.simulation.MAX_STEPS](MAX_STEPS.md) - Constant `MAX_STEPS` in `application/simulation`.
* [application.simulation.NEW_RECORD](NEW_RECORD.md) - Constant `NEW_RECORD` in `application/simulation`.
* [application.simulation.SLIP](SLIP.md) - Constant `SLIP` in `application/simulation`.
* [application.simulation.STALE](STALE.md) - Constant `STALE` in `application/simulation`.
* [application.simulation.TRACE_LIMIT](TRACE_LIMIT.md) - Constant `TRACE_LIMIT` in `application/simulation`.

# Functions

* [application.simulation.run_log](run_log.md) - Every step of the seeded run in order, and where a run with these breakpoints stops (ADR-0160).
* [application.simulation.simulate](simulate.md) - Run `steps` seeded attempts by the pack's fixture actors through the kernel and report where they went.

# Methods

* [application.simulation.MemorySession.actor](MemorySession.actor.md) - `def actor(self, actor_id: str) -> dict[str, Any]` in `application/simulation`.
* [application.simulation.MemorySession.create_instance](MemorySession.create_instance.md) - `def create_instance(self, item: dict[str, Any]) -> None` in `application/simulation`.
* [application.simulation.MemorySession.enqueue](MemorySession.enqueue.md) - `def enqueue(self, case_id: str, operation_id: str, effect: str, recipient: str) -> None` in `application/simulation`.
* [application.simulation.MemorySession.event](MemorySession.event.md) - `def event(self, kind: str, body: dict[str, Any]) -> None` in `application/simulation`.
* [application.simulation.MemorySession.find_instance](MemorySession.find_instance.md) - `def find_instance(self, instance_id: str, case_id: str) -> dict[str, Any] | None` in `application/simulation`.
* [application.simulation.MemorySession.find_operation](MemorySession.find_operation.md) - `def find_operation(self, operation_id: str) -> dict[str, Any] | None` in `application/simulation`.
* [application.simulation.MemorySession.record_operation](MemorySession.record_operation.md) - `def record_operation(self, operation_id: str, binding: str, result: dict[str, Any]) -> None` in `application/simulation`.
* [application.simulation.MemorySession.update_instance](MemorySession.update_instance.md) - `def update_instance(self, item: dict[str, Any], expected: int) -> None` in `application/simulation`.
