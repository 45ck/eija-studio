# Symbols of application.oracle_session

# Classes

* [application.oracle_session.OracleSession](OracleSession.md) - In-memory answers to exactly the port calls `execute` makes for one instance.

# Constants

* [application.oracle_session.UNKNOWN_ACTOR](UNKNOWN_ACTOR.md) - Constant `UNKNOWN_ACTOR` in `application/oracle_session`.

# Functions

* [application.oracle_session.absent](absent.md) - A name guaranteed not to be in `taken`, so a negative case can never collide with a declared one.
* [application.oracle_session.kernel_answer](kernel_answer.md) - `def kernel_answer(pack: Pack, model: Workflow, session: OracleSession, actor: str, action: str, version: int,…` in `application/oracle_session`.

# Methods

* [application.oracle_session.OracleSession.actor](OracleSession.actor.md) - `def actor(self, actor_id: str) -> dict[str, Any]` in `application/oracle_session`.
* [application.oracle_session.OracleSession.acts](OracleSession.acts.md) - `def acts(self, instance_id: str) -> list[tuple[str, str]]` in `application/oracle_session`.
* [application.oracle_session.OracleSession.create_instance](OracleSession.create_instance.md) - `def create_instance(self, item: dict[str, Any]) -> None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.elapsed](OracleSession.elapsed.md) - `def elapsed(self, instance_id: str) -> float | None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.enqueue](OracleSession.enqueue.md) - `def enqueue(self, case_id: str, operation_id: str, effect: str, recipient: str) -> None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.event](OracleSession.event.md) - `def event(self, kind: str, body: dict[str, Any]) -> None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.find_instance](OracleSession.find_instance.md) - `def find_instance(self, instance_id: str, case_id: str) -> dict[str, Any] | None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.find_operation](OracleSession.find_operation.md) - `def find_operation(self, operation_id: str) -> dict[str, Any] | None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.record_act](OracleSession.record_act.md) - `def record_act(self, instance_id: str, action: str, actor_id: str) -> None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.record_operation](OracleSession.record_operation.md) - `def record_operation(self, operation_id: str, binding: str, result: dict[str, Any]) -> None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.update_instance](OracleSession.update_instance.md) - `def update_instance(self, item: dict[str, Any], expected: int) -> None` in `application/oracle_session`.
* [application.oracle_session.OracleSession.values](OracleSession.values.md) - `def values(self, instance_id: str) -> dict[str, Any]` in `application/oracle_session`.
