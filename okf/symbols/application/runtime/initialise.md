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
  sha256: ae32000717d985326c65d9f1b40bf992ffc11fc2d69ee9a340ab0c1986e67591
description_override: Creates an isolated preview instance bound to a model hash at version 0, after the policy check.
notes_baseline: 1542cd517ce45d9c4089f766abc792314ccd6ebe42931854b8bdc37b076ac05a
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
---

# application.runtime.initialise

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/runtime`](/modules/application/runtime.md) |
| Signature | `def initialise(session: UnitOfWork, case_id: str, model: Workflow, *, state: str \| None=None, pack: Pack \| None=None) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/runtime.py#initialise` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

A changed candidate makes the instance stale; reset creates a new instance instead of migrating the old one ([Preview Instance](/language/preview-instance.md)).

<!-- okf:generated:begin links -->
## Depends on

* [application.memo.ensure_conforms](/symbols/application/memo/ensure_conforms.md) - `ensure(model, pack)` (the policy check): a pair it let through is remembered; any other is refused by it again, so the error is always the check's own.
* [application.memo.model_hash](/symbols/application/memo/model_hash.md) - `model.semantic_hash`, computed once per model object.
* [application.ports.UnitOfWork](/symbols/application/ports/UnitOfWork.md) - All mutations on this port commit together or roll back together.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.default_pack](/symbols/domain/pack/default_pack.md) - The configured pack, reread on every call and validated from a content-keyed cache.
* [domain.policy.ensure_policy](/symbols/domain/policy/ensure_policy.md) - `def ensure_policy(model: Workflow, pack: Pack | None=None) -> None` in `domain/policy`.

## Referenced by

* [application.service.Studio.reset_preview](/symbols/application/service/Studio.reset_preview.md) - `def reset_preview(self, case_id: str, expected: int, state: str | None=None) -> dict[str, Any]` in `application/service`.
<!-- okf:generated:end links -->
