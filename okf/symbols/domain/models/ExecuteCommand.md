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
notes_baseline: a2a117be9176ce6df5636b2c58c81279923101006e80d95682985834ffcdb0d9
---

# domain.models.ExecuteCommand

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `class ExecuteCommand(Contract)` |
| Code | `repo://src/eija_studio/domain/models.py#ExecuteCommand` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

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

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [Execution](/contexts/execution.md) - Owns Trusted fixture actor state, preview instances, command replay, committed effect intents
* [application.diagrams.CONTRACTS](/symbols/application/diagrams/CONTRACTS.md) - Constant `CONTRACTS` in `application/diagrams`.
* [application.runtime.check_actor](/symbols/application/runtime/check_actor.md) - `def check_actor(actor: dict[str, Any], transition: Transition, command: ExecuteCommand) -> None` in `application/runtime`.
* [application.runtime.execute](/symbols/application/runtime/execute.md) - `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault: Callable[[…` in `application/runtime`.
* [application.service.Studio.execute](/symbols/application/service/Studio.execute.md) - `def execute(self, case_id: str, command: ExecuteCommand, fault: Callable[[str], None] | None=None) -> dict[st…` in `application/service`.
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio` in `application/service`.
<!-- okf:generated:end links -->
