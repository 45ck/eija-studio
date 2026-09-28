---
type: Function
title: application.runtime.execute
description: 'Executes one command against a preview instance: authority is checked before replay, versions are compare-and-swap, and audit and outbox commit with the state change.'
resource: repo://src/eija_studio/application/runtime.py#execute
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/runtime.py#execute
  title: application/runtime.py
  hash_method: ast-v1
  sha256: 5d8b324a729caf40ebd92e0fdc536a570b73fe6077dd39e0f9b7d5e54ded4265
description_override: 'Executes one command against a preview instance: authority is checked before replay, versions are compare-and-swap, and audit and outbox commit with the state change.'
---

# application.runtime.execute

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/runtime`](/modules/application/runtime.md) |
| Signature | `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault=None) -> dict` |
| Code | `repo://src/eija_studio/application/runtime.py#execute` |
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

The commit sequence, in the order the code performs it:

1. `ensure_policy` and model-identity check (`STALE_INSTANCE`).
2. **Authorise first** with [check_actor](/symbols/application/runtime/check_actor.md): active, current role, and assignment where the guard requires it. A cached success is not continuing authority.
3. Replay: an existing operation id with a different binding is `OPERATION_CONFLICT`; the same binding returns the original result and enqueues nothing again.
4. Version and source-state guards (`STALE_VERSION`, `STATE_DENIED`), then the state update.
5. Required effects: `Audit:*` rows and `Notification:*` outbox intents in the same unit of work, then `record_operation`.

Success is reported to HTTP only after the enclosing [UnitOfWork](/symbols/application/ports/UnitOfWork.md) commits; an exception rolls everything back. This is an at-most-once *local enqueue* guarantee ([Effect Intent](/language/effect-intent.md)), not external delivery. The optional `fault` hook exists so tests can crash after each step (acceptance [AC11](/requirements/ac11.md), [AC14](/requirements/ac14.md)).

<!-- okf:generated:begin links -->
## Depends on

* [application.ports.UnitOfWork](/symbols/application/ports/UnitOfWork.md) - All mutations on this port commit together or roll back together.
* [application.runtime.check_actor](/symbols/application/runtime/check_actor.md) - `def check_actor(actor: dict, transition, command: ExecuteCommand) -> None` in `application/runtime` (the source has no docstring).
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.ExecuteCommand](/symbols/domain/models/ExecuteCommand.md) - `class ExecuteCommand(Contract)` in `domain/models` (the source has no docstring).
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models` (the source has no docstring).
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models` (the source has no docstring).
* [domain.policy.ensure_policy](/symbols/domain/policy/ensure_policy.md) - `def ensure_policy(model: Workflow) -> None` in `domain/policy` (the source has no docstring).

## Referenced by

* [application.service.Studio.execute](/symbols/application/service/Studio.execute.md) - `def execute(self, case_id: str, command: ExecuteCommand, fault=None) -> dict` in `application/service` (the source has no docstring).
* [application.verifier.verify_runtime](/symbols/application/verifier/verify_runtime.md) - `def verify_runtime(model: Workflow, subject: dict, sandbox: SandboxFactory) -> dict` in `application/verifier` (the source has no docstring).
<!-- okf:generated:end links -->
