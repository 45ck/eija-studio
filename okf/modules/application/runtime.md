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
  sha256: 7eeff32ad25a826b1731d2419dc9c58d18024d900cd3dca96dc78417eab0214e
notes_baseline: 9d31a53e89078de2a5032d154a576e7a9fdfc3ec8dd2f71594d299c6b61e04da
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
* [application.runtime.check_actor](/symbols/application/runtime/check_actor.md) - `def check_actor(actor: dict, transition, command: ExecuteCommand) -> None` in `application/runtime`.
* [application.runtime.execute](/symbols/application/runtime/execute.md) - `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault=None) -> di…` in `application/runtime`.
* [application.runtime.initialise](/symbols/application/runtime/initialise.md) - `def initialise(session: UnitOfWork, case_id: str, model: Workflow, *, state: str | None=None) -> dict` in `application/runtime`.
<!-- okf:generated:end links -->
