---
type: Function
title: application.runtime.initialise
description: Creates an isolated preview instance bound to a model hash at version 0, after the policy check.
resource: repo://src/eija_studio/application/runtime.py#initialise
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/runtime.py#initialise
  title: application/runtime.py
  hash_method: ast-v2
  sha256: 83b3bd6120c30aefbc6eeec03fc7a7a6051f89731eb7fafac3e1552504252871
description_override: Creates an isolated preview instance bound to a model hash at version 0, after the policy check.
notes_baseline: 54cd2f03a97cec02f27a5db17192164f5d7f1eeaec9d3d52c9b070ef86766b69
verified:
- by: process:claude-code-integration-phase0
  at: '2026-09-29T04:30:00Z'
  notes_sha256: 9469f61f318d2fb0871f23aed6c62eedb90c39d4811dc8c723af165ef60ba35c
  sources_sha256: a7fb3056b1f349861bc302e97cb8f880ccd73a1cfce96d0f7da8bf1651c0a2e6
- by: process:eija-wbs-1.3-agent
  at: '2026-09-29T08:20:47Z'
  notes_sha256: 9469f61f318d2fb0871f23aed6c62eedb90c39d4811dc8c723af165ef60ba35c
  sources_sha256: 24c83ebfb1ec46af0dd84eb62bfc5354f84a37fb27722270e7b29c2721a8cad4
- by: process:claude-undo-autosave
  at: '2026-10-08T23:55:00Z'
  notes_sha256: 9469f61f318d2fb0871f23aed6c62eedb90c39d4811dc8c723af165ef60ba35c
  sources_sha256: 1542cd517ce45d9c4089f766abc792314ccd6ebe42931854b8bdc37b076ac05a
- by: process:claude-code
  at: '2026-11-11T12:00:00Z'
  notes_sha256: 9539d1eb64ce9ef5e67edc1c5d8bf22e7e6ecb51cf238018332b66c091702f1c
  sources_sha256: 496d6be764ff839c996699573601ebc078f196ddd5c9016a3494d1f0fdc48704
- by: process:kernel-inspection
  at: '2026-11-14T02:00:00Z'
  notes_sha256: aca98502efbab7aa3d0d18240f6875d4f4867a36822acf80d507bb14d39a2b9e
  sources_sha256: 54cd2f03a97cec02f27a5db17192164f5d7f1eeaec9d3d52c9b070ef86766b69
---

# application.runtime.initialise

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/runtime`](/modules/application/runtime.md) |
| Signature | `def initialise(session: UnitOfWork, case_id: str, model: Workflow, *, state: str \| None=None, pack: Pack \| None=None, role: str \| None=None, actor_id: str \| None=None) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/runtime.py#initialise` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Start a record. With ``actor_id`` the creator must be a known, active actor (ADR-0250), and their role is the
one judged; with ``role`` alone, that role. A model that names its initiators refuses any other role (ADR-0231).
With neither, the caller is a preview or oracle that starts records on the kernel's behalf.
~~~
<!-- okf:generated:end facts -->

## Notes

A changed candidate makes the instance stale; reset creates a new instance instead of migrating the old one ([Preview Instance](/language/preview-instance.md)). Given the creator's `actor_id`, an unknown actor is `UNKNOWN_ACTOR` and a revoked one `ACTOR_REVOKED`, as for an action, and their role is the one judged ([ADR-0250](/adrs/0250-kernel-second-inspection.md)). Given a `role` (or an actor), a model that names its initiators refuses anyone else with `ROLE_CANNOT_START` and writes nothing (ADR-0231); with neither there is no check (previews and oracles). A model named for another pack is `WORKFLOW_PACK_MISMATCH`.

<!-- okf:generated:begin links -->
## Depends on

* [application.memo.model_hash](/symbols/application/memo/model_hash.md) - `model.semantic_hash`, computed once per model object.
* [application.ports.UnitOfWork](/symbols/application/ports/UnitOfWork.md) - All mutations on this port commit together or roll back together.
* [application.runtime.check_starter](/symbols/application/runtime/check_starter.md) - The role of the actor starting a record: an unknown actor is refused by the directory and a revoked one as it is refused an action (ADR-0250), so whoever start…
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.default_pack](/symbols/domain/pack/default_pack.md) - The configured pack, reread on every call and validated from a content-keyed cache.

## Referenced by

* [application.app_runs.create_cases](/symbols/application/app_runs/create_cases.md) - Every fixture actor, and one unknown actor, starting a record with valid values: the state and version it starts in, or the refusal.
* [application.runtime.receive](/symbols/application/runtime/receive.md) - Start a record because another workflow of the system sent `signal` (issue #93 item 5, ADR-0242).
* [application.service.Studio.reset_preview](/symbols/application/service/Studio.reset_preview.md) - `def reset_preview(self, case_id: str, expected: int, state: str | None=None) -> dict[str, Any]` in `application/service`.
<!-- okf:generated:end links -->
