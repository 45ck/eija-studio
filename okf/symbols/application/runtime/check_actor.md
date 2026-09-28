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
  hash_method: ast-v1
  sha256: 4226662321fa38707e0e8f0b1e9f959301dcd6178b09c3e9973c7594841c4a17
description_override: Denies a command unless the trusted actor is active, holds the transition's role and, where guarded, is assigned.
---

# application.runtime.check_actor

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/runtime`](/modules/application/runtime.md) |
| Signature | `def check_actor(actor: dict, transition, command: ExecuteCommand) -> None` |
| Code | `repo://src/eija_studio/application/runtime.py#check_actor` |
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Raises `ACTOR_REVOKED`, `ROLE_DENIED` or `ASSIGNMENT_DENIED`. Called from [execute](/symbols/application/runtime/execute.md) before replay, which is what makes revocation after preview effective at commit time.

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.ExecuteCommand](/symbols/domain/models/ExecuteCommand.md) - `class ExecuteCommand(Contract)` in `domain/models` (the source has no docstring).

## Referenced by

* [application.runtime.execute](/symbols/application/runtime/execute.md) - `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault=None) -> dict` in `application/runtime` (the source has no d…
<!-- okf:generated:end links -->
