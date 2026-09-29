---
type: Function
title: application.runtime.check_actor
description: Denies a command unless the trusted actor is active, holds the transition's role and, where guarded, is assigned.
resource: repo://src/eija_studio/application/runtime.py#check_actor
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/runtime.py#check_actor
  title: application/runtime.py
  hash_method: ast-v2
  sha256: ce8cdbafa118c1fd015da3af28de070c1784658e205dd28179f6c4f2c8e985c3
description_override: Denies a command unless the trusted actor is active, holds the transition's role and, where guarded, is assigned.
notes_baseline: d55ffbf9987829aebc45beaec5e74faa8d397a4c675df42d407517a92d77dbc1
---

# application.runtime.check_actor

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/runtime`](/modules/application/runtime.md) |
| Signature | `def check_actor(actor: dict[str, Any], transition: Transition, command: ExecuteCommand) -> None` |
| Code | `repo://src/eija_studio/application/runtime.py#check_actor` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Raises `ACTOR_REVOKED`, `ROLE_DENIED` or `ASSIGNMENT_DENIED`. Called from [execute](/symbols/application/runtime/execute.md) before replay, which is what makes revocation after preview effective at commit time.

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.ExecuteCommand](/symbols/domain/models/ExecuteCommand.md) - `class ExecuteCommand(Contract)` in `domain/models`.
* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models`.

## Referenced by

* [application.runtime.execute](/symbols/application/runtime/execute.md) - `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault: Callable[[…` in `application/runtime`.
<!-- okf:generated:end links -->
