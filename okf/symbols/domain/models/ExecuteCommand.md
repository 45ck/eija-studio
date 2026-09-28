---
type: Class
title: domain.models.ExecuteCommand
description: A preview command bound to an operation id, actor, instance, action and expected version.
resource: repo://src/eija_studio/domain/models.py#ExecuteCommand
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#ExecuteCommand
  title: domain/models.py
  hash_method: ast-sig-v1
  sha256: 48b5954daef1d067ad22c9808aba5ec51cda6abfe17aa1aa88e93992eae3d285
description_override: A preview command bound to an operation id, actor, instance, action and expected version.
---

# domain.models.ExecuteCommand

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `class ExecuteCommand(Contract)` |
| Code | `repo://src/eija_studio/domain/models.py#ExecuteCommand` |
| Hash | `ast-sig-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `operation_id` | `str` | `Field(pattern='^[A-Za-z0-9_-]{1,100}$')` |
| `actor_id` | `str` | `Field(min_length=1, max_length=80)` |
| `instance_id` | `str` | `Field(min_length=1, max_length=80)` |
| `action` | `str` | `Field(min_length=1, max_length=60)` |
| `expected_version` | `int` | `Field(ge=0, strict=True)` |
<!-- okf:generated:end facts -->

## Notes

All five fields form the replay binding checked in [runtime.execute](/symbols/application/runtime/execute.md); `expected_version` is strict-int so a stale caller is rejected, not coerced.

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models` (the source has no docstring).

## Referenced by

* [Execution](/contexts/execution.md) - Owns Trusted fixture actor state, preview instances, command replay, committed effect intents
* [application.runtime.check_actor](/symbols/application/runtime/check_actor.md) - `def check_actor(actor: dict, transition, command: ExecuteCommand) -> None` in `application/runtime` (the source has no docstring).
* [application.runtime.execute](/symbols/application/runtime/execute.md) - `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault=None) -> dict` in `application/runtime` (the source has no d…
* [application.service.Studio.execute](/symbols/application/service/Studio.execute.md) - `def execute(self, case_id: str, command: ExecuteCommand, fault=None) -> dict` in `application/service` (the source has no docstring).
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio` in `application/service` (the source has no docstring).
* [application.verifier.verify_runtime](/symbols/application/verifier/verify_runtime.md) - `def verify_runtime(model: Workflow, subject: dict, sandbox: SandboxFactory) -> dict` in `application/verifier` (the source has no docstring).
<!-- okf:generated:end links -->
