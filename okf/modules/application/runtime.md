---
type: Module
title: application.runtime
description: Generic execution algorithm; domain-specific policy stays in domain.policy.
resource: repo://src/eija_studio/application/runtime.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/runtime.py
  title: application/runtime.py
  hash_method: ast-api-v1
  sha256: 3e0c7687a7422100541ca159b8ce5eecf5d923b44745759eaf97d564a2528fd2
notes_baseline: 53b19591611a7dfe565f6dd979e1c7e52bb3d1a74bf852d4a4bcd45b7f492043
verified:
- by: process:claude-code-integration-phase0
  at: '2026-09-29T04:30:00Z'
  notes_sha256: 090429967737d6a66e5f0cbb10b99a1a5ee88b4f6ad6a9bf32a21c2776eba1f7
  sources_sha256: 53b19591611a7dfe565f6dd979e1c7e52bb3d1a74bf852d4a4bcd45b7f492043
---

# application.runtime

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/runtime.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Generic execution algorithm; domain-specific policy stays in domain.policy.
~~~

## Public symbols

* [`check_actor`](/symbols/application/runtime/check_actor.md) (function) - no docstring
* [`execute`](/symbols/application/runtime/execute.md) (function) - no docstring
* [`initialise`](/symbols/application/runtime/initialise.md) (function) - no docstring

## Internal imports

* [`application/ports`](/modules/application/ports.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/policy`](/modules/domain/policy.md)
<!-- okf:generated:end facts -->

## Notes

The generic execution algorithm; domain-specific policy stays in [domain.policy](/modules/domain/policy.md).

<!-- okf:generated:begin links -->
## Imports

* [application.ports](/modules/application/ports.md) - Application-owned ports.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.policy](/modules/domain/policy.md) - Protected excursion policy.

## Referenced by

* [Execution](/contexts/execution.md) - Owns Trusted fixture actor state, preview instances, command replay, committed effect intents
* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
* [application.verifier](/modules/application/verifier.md) - Bounded synthetic runtime experiments.
* [application.runtime.check_actor](/symbols/application/runtime/check_actor.md) - `def check_actor(actor: dict[str, Any], transition: Transition, command: ExecuteCommand) -> None` in `application/runtime`.
* [application.runtime.execute](/symbols/application/runtime/execute.md) - `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault: Callable[[…` in `application/runtime`.
* [application.runtime.initialise](/symbols/application/runtime/initialise.md) - `def initialise(session: UnitOfWork, case_id: str, model: Workflow, *, state: str | None=None) -> dict[str, An…` in `application/runtime`.
<!-- okf:generated:end links -->
