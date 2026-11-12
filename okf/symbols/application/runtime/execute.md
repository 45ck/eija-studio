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
  sha256: 1daae9ffa274b22eed0a022308bdfe1fce49e791a65618e111765a428d27db37
description_override: 'Executes one command against a preview instance: authority is checked before replay, versions are compare-and-swap, and audit and outbox commit with the state change.'
notes_baseline: 585b3c807e68801a3cf09dfbf68c55727320b52f675fa0c69a16acec50203f1e
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
- by: process:claude-code
  at: '2026-11-11T13:00:00Z'
  notes_sha256: dfe04ae0f939b3dc6f5f14024f1734fc5143e74a17b0b76f63eaa874ed4c6a37
  sources_sha256: 127bca8128bc242ceeb420ee22c625071d98f51df4452d0744be292adc7f10a9
- by: process:claude-code
  at: '2026-11-11T12:00:00Z'
  notes_sha256: b48429d3549b75841f9905147dcbe4b998f26a44b506014f8768ddf0f70b6859
  sources_sha256: 7154b62fb58e39e64733d109ee208f7e75cdb0d74bc9a6656aab54d071c76354
- by: process:claude-code
  at: '2026-11-11T12:30:00Z'
  notes_sha256: b48429d3549b75841f9905147dcbe4b998f26a44b506014f8768ddf0f70b6859
  sources_sha256: 3a95c13fc45694f0ddd526f38de4d0522fc0a24e813c639a82a1ddebf2f5ca73
- by: process:claude-code
  at: '2026-11-11T22:00:00Z'
  notes_sha256: 795a6b25112a3ab6372c464619270e82ac1f11dd1f72b85b79c17bd78c6ab320
  sources_sha256: 55b9d1c43a76ddc897f38689e389f9ed0e5c1e190c97581b6d7258f6cb810b2c
- by: process:claude-code
  at: '2026-11-12T03:00:00Z'
  notes_sha256: cbc43b666ea096285752a3d9a2c9681d40d3d6ccb23c5609db57dfee4651819b
  sources_sha256: 62a73d42ad3ec3ab9b76effd54435c9574c8e556511580dce5f88f9528fa7e74
- by: process:claude-code
  at: '2026-11-12T04:00:08Z'
  notes_sha256: 6a221897ae96cef4faaf5cd38fff1d7a8bc938d919f25007fe725fdac1f42593
  sources_sha256: 585b3c807e68801a3cf09dfbf68c55727320b52f675fa0c69a16acec50203f1e
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

The transition is the one the command's action takes from the record's state; an action may leave several states, all alike but for their source, so authority does not depend on which one ([ADR-0232](/adrs/0232-one-action-from-several-states.md)). The commit sequence, in the order the code performs it:
1. `ensure_policy` (under the pack) and model-identity check (`STALE_INSTANCE`). Both go through [application.memo](/modules/application/memo.md), which asks them once per frozen model and pack object; a refusal still comes from `ensure_policy` itself ([ADR-0199](/adrs/0199-playide-at-the-kernel-limits.md)).
2. **Authorise first** with [check_actor](/symbols/application/runtime/check_actor.md): active, current role, and assignment where the guard requires it. A cached success is not continuing authority.
3. Replay: an existing operation id with a different binding is `OPERATION_CONFLICT`; the same binding returns the original result and enqueues nothing again.
4. Version and source-state guards (`STALE_VERSION`, `STATE_DENIED`). Then the transition's time event, read through `UnitOfWork.elapsed` only when it has one (`TIMER_NOT_DUE`, [ADR-0237](/adrs/0237-time-events.md)). Then the transition's guards over record values, read through `UnitOfWork.values` only when it has them (`VALUE_GUARD_DENIED`, [ADR-0234](/adrs/0234-guards-over-record-values.md)). Then separation of duties, only when a `distinct_actors` law in force names the action: an actor who already took another of its actions on this record is `SEPARATION_DENIED`, and otherwise the act is logged in the same unit of work ([ADR-0233](/adrs/0233-separation-of-duties.md)). Steps on linked objects are checked before separation of duties, only when the transition has `then`: each object's state is read through `UnitOfWork.object_state`, and an object with no move for the event from its state, or with no state, is `LINKED_OBJECT_REFUSED` ([ADR-0241](/adrs/0241-actions-on-linked-objects.md)). Then the state update, and each object's move through `UnitOfWork.move_object` in the same unit of work; the result lists `moved`.
5. Required effects, typed by the pack: an `audit` effect is an event row, a `notification` effect an outbox intent for its declared recipient, both in the same unit of work, then `record_operation`. An effect the pack does not declare is `EFFECT_DENIED`.

Success is reported to HTTP only after the enclosing [UnitOfWork](/symbols/application/ports/UnitOfWork.md) commits; an exception rolls everything back. This is an at-most-once *local enqueue* guarantee ([Effect Intent](/language/effect-intent.md)), not external delivery. The optional `fault` hook exists so tests can crash after each step (acceptance [AC11](/requirements/ac11.md), [AC14](/requirements/ac14.md)).

<!-- okf:generated:begin links -->
## Depends on

* [application.memo.ensure_conforms](/symbols/application/memo/ensure_conforms.md) - `ensure(model, pack)` (the policy check): a pair it let through is remembered; any other is refused by it again, so the error is always the check's own.
* [application.memo.model_hash](/symbols/application/memo/model_hash.md) - `model.semantic_hash`, computed once per model object.
* [application.ports.UnitOfWork](/symbols/application/ports/UnitOfWork.md) - All mutations on this port commit together or roll back together.
* [application.runtime.check_actor](/symbols/application/runtime/check_actor.md) - `def check_actor(actor: dict[str, Any], transition: Transition, command: ExecuteCommand) -> None` in `application/runtime`.
* [application.runtime.separations](/symbols/application/runtime/separations.md) - The pack's separation-of-duties laws in force on ``model`` that name ``action`` (issue #149, ADR-0233).
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
