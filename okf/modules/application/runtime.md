---
type: Module
title: application.runtime
description: Generic execution algorithm; the domain (policy, laws, typed effects) comes from the pack.
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
  sha256: 3899636ca8052d37e8ad2b090e55beacf6b38f1bb91c23f915769661901a1441
notes_baseline: d7a2e4e86517ea444c8094a627d3ae1944555e5143febf2a41e37ed024136ce1
verified:
- by: process:claude-code-integration-phase0
  at: '2026-09-29T04:30:00Z'
  notes_sha256: 090429967737d6a66e5f0cbb10b99a1a5ee88b4f6ad6a9bf32a21c2776eba1f7
  sources_sha256: 53b19591611a7dfe565f6dd979e1c7e52bb3d1a74bf852d4a4bcd45b7f492043
- by: process:eija-wbs-1.3-agent
  at: '2026-09-29T08:20:47Z'
  notes_sha256: 51ed90c46c69260b371ab2a1d5139bf24f4f09c768aa115ebe4f70f4d761e6bb
  sources_sha256: d7a2e4e86517ea444c8094a627d3ae1944555e5143febf2a41e37ed024136ce1
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
Generic execution algorithm; the domain (policy, laws, typed effects) comes from the pack.
~~~

## Public symbols

* [`check_actor`](/symbols/application/runtime/check_actor.md) (function) - no docstring
* [`execute`](/symbols/application/runtime/execute.md) (function) - no docstring
* [`initialise`](/symbols/application/runtime/initialise.md) (function) - no docstring

## Internal imports

* [`application/memo`](/modules/application/memo.md)
* [`application/ports`](/modules/application/ports.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/policy`](/modules/domain/policy.md)
<!-- okf:generated:end facts -->

## Notes

The generic execution algorithm. Policy, laws and typed effects come from the domain pack ([domain.pack](/modules/domain/pack.md), [domain.policy](/modules/domain/policy.md)); nothing here names a domain.

<!-- okf:generated:begin links -->
## Imports

* [application.memo](/modules/application/memo.md) - Ask the kernel the same question of the same frozen model once (ADR-0199).
* [application.ports](/modules/application/ports.md) - Application-owned ports.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.policy](/modules/domain/policy.md) - Generic policy: coherence with a domain pack's declared action catalog, the pack's laws, and declared effects.

## Referenced by

* [Execution](/contexts/execution.md) - Owns Trusted fixture actor state, preview instances, command replay, committed effect intents
* [application.access](/modules/application/access.md) - Who can do what (ADR-0171): the model's permissions as a role by state matrix, each cell checked by the kernel, and reachability questions such as "can a recor…
* [application.appgen](/modules/application/appgen.md) - App generation: a reviewed workflow model becomes a runnable app and its conformance oracle (ADR-0150).
* [application.review](/modules/application/review.md) - Review a model change in PlayIDE instead of a pull request (ADR-0175).
* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
* [application.simulation](/modules/application/simulation.md) - Seeded simulation of people using the app built from a model (ADR-0152).
* [application.verifier](/modules/application/verifier.md) - Bounded synthetic runtime experiments.
* [application.runtime.check_actor](/symbols/application/runtime/check_actor.md) - `def check_actor(actor: dict[str, Any], transition: Transition, command: ExecuteCommand) -> None` in `application/runtime`.
* [application.runtime.execute](/symbols/application/runtime/execute.md) - `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault: Callable[[…` in `application/runtime`.
* [application.runtime.initialise](/symbols/application/runtime/initialise.md) - `def initialise(session: UnitOfWork, case_id: str, model: Workflow, *, state: str | None=None, pack: Pack | No…` in `application/runtime`.
<!-- okf:generated:end links -->
