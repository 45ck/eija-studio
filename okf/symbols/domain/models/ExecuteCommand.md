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
  sha256: 23a9c51aa6888993ab4ced847723eaf9615882bd795dc839ac40416e4a94c56e
description_override: A preview command bound to an operation id, actor, instance, action and expected version.
notes_baseline: 5a6e5cd14ec42545f500993c140d89cfe03e7e58ecf3d159ce6246360fa4c6fa
verified:
- by: process:claude-code
  at: '2026-11-12T03:20:00Z'
  notes_sha256: 9176e25a115f902fc1c75eb295facbb936efc4c5a6e0408aeaafc257cce9a273
  sources_sha256: 5a6e5cd14ec42545f500993c140d89cfe03e7e58ecf3d159ce6246360fa4c6fa
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
| `expected_version` | `JsonInt` | `Field(ge=0)` |
<!-- okf:generated:end facts -->

## Notes

All five fields form the replay binding checked in [runtime.execute](/symbols/application/runtime/execute.md); `expected_version` is a JSON integer ([JsonInt](/symbols/domain/models/JsonInt.md), ADR-0238): an int or a float with no fractional part such as `1.0`, never a string or a boolean, so a stale caller is rejected, not coerced from text.

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.models.JsonInt](/symbols/domain/models/JsonInt.md) - Type alias `JsonInt` in `domain/models`.

## Referenced by

* [Execution](/contexts/execution.md) - Owns Trusted fixture actor state, preview instances, command replay, committed effect intents
* [application.diagrams.CONTRACTS](/symbols/application/diagrams/CONTRACTS.md) - Constant `CONTRACTS` in `application/diagrams`.
* [application.runtime.check_actor](/symbols/application/runtime/check_actor.md) - `def check_actor(actor: dict[str, Any], transition: Transition, command: ExecuteCommand) -> None` in `application/runtime`.
* [application.runtime.execute](/symbols/application/runtime/execute.md) - `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault: Callable[[…` in `application/runtime`.
* [application.service.Studio.execute](/symbols/application/service/Studio.execute.md) - `def execute(self, case_id: str, command: ExecuteCommand, fault: Callable[[str], None] | None=None) -> dict[st…` in `application/service`.
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio(StudioViews)` in `application/service`.
<!-- okf:generated:end links -->
