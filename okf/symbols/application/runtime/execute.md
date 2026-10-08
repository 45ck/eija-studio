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
  hash_method: ast-v2
  sha256: 5d688ada90b700ecc0b317423ce7279ec4c2709979192f9d86a511f383b44ac4
description_override: 'Executes one command against a preview instance: authority is checked before replay, versions are compare-and-swap, and audit and outbox commit with the state change.'
notes_baseline: 873d2643fe7445b3c19bf0d24ea2160e5f314eb805620aa111859af671bf09ed
verified:
- by: process:claude-code-integration-phase0
  at: '2026-09-29T04:30:00Z'
  notes_sha256: 74d191e8403a93cba1b318cdf280ab7320daa213ed6f023aedf0a9a09986ae68
  sources_sha256: 916058b8d6b5dee1c03f0f144b91b10a2bed759ff5647993b8d3aceb0f4649a2
- by: process:eija-wbs-1.3-agent
  at: '2026-09-29T08:20:47Z'
  notes_sha256: 779b0aea4964ffceb958b09cbf1768072f7933ac0520e656e59dc97e391ced99
  sources_sha256: 3125a6d9934abf25f66651366fd598a356cea8b7c0d7234dbb705443424b942d
- by: process:claude-undo-autosave
  at: '2026-10-08T23:55:00Z'
  notes_sha256: d7ed99eb19af019c570df3e501f157e6b7a2759675bb3c3e589bbfab400a3585
  sources_sha256: 873d2643fe7445b3c19bf0d24ea2160e5f314eb805620aa111859af671bf09ed
---

# application.runtime.execute

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/runtime`](/modules/application/runtime.md) |
| Signature | `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault: Callable[[str], None] \| None=None, pack: Pack \| None=None) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/runtime.py#execute` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

The commit sequence, in the order the code performs it:
1. `ensure_policy` (under the pack) and model-identity check (`STALE_INSTANCE`). Both go through [application.memo](/modules/application/memo.md), which asks them once per frozen model and pack object; a refusal still comes from `ensure_policy` itself ([ADR-0199](/adrs/0199-playide-at-the-kernel-limits.md)).
2. **Authorise first** with [check_actor](/symbols/application/runtime/check_actor.md): active, current role, and assignment where the guard requires it. A cached success is not continuing authority.
3. Replay: an existing operation id with a different binding is `OPERATION_CONFLICT`; the same binding returns the original result and enqueues nothing again.
4. Version and source-state guards (`STALE_VERSION`, `STATE_DENIED`), then the state update.
5. Required effects, typed by the pack: an `audit` effect is an event row, a `notification` effect an outbox intent for its declared recipient, both in the same unit of work, then `record_operation`. An effect the pack does not declare is `EFFECT_DENIED`.

Success is reported to HTTP only after the enclosing [UnitOfWork](/symbols/application/ports/UnitOfWork.md) commits; an exception rolls everything back. This is an at-most-once *local enqueue* guarantee ([Effect Intent](/language/effect-intent.md)), not external delivery. The optional `fault` hook exists so tests can crash after each step (acceptance [AC11](/requirements/ac11.md), [AC14](/requirements/ac14.md)).

<!-- okf:generated:begin links -->
## Depends on

* [application.memo.ensure_conforms](/symbols/application/memo/ensure_conforms.md) - `ensure(model, pack)` (the policy check): a pair it let through is remembered; any other is refused by it again, so the error is always the check's own.
* [application.memo.model_hash](/symbols/application/memo/model_hash.md) - `model.semantic_hash`, computed once per model object.
* [application.ports.UnitOfWork](/symbols/application/ports/UnitOfWork.md) - All mutations on this port commit together or roll back together.
* [application.runtime.check_actor](/symbols/application/runtime/check_actor.md) - `def check_actor(actor: dict[str, Any], transition: Transition, command: ExecuteCommand) -> None` in `application/runtime`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.ExecuteCommand](/symbols/domain/models/ExecuteCommand.md) - `class ExecuteCommand(Contract)` in `domain/models`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.default_pack](/symbols/domain/pack/default_pack.md) - The configured pack, reread on every call and validated from a content-keyed cache.
* [domain.policy.ensure_policy](/symbols/domain/policy/ensure_policy.md) - `def ensure_policy(model: Workflow, pack: Pack | None=None) -> None` in `domain/policy`.

## Referenced by

* [application.service.Studio.execute](/symbols/application/service/Studio.execute.md) - `def execute(self, case_id: str, command: ExecuteCommand, fault: Callable[[str], None] | None=None) -> dict[st…` in `application/service`.
<!-- okf:generated:end links -->
