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
  sha256: 1f3094bd90c52113be7d3cc8977d3edd363170b286a35a946e8831e043ecfeee
description_override: Creates an isolated preview instance bound to a model hash at version 0, after the policy check.
notes_baseline: a7fb3056b1f349861bc302e97cb8f880ccd73a1cfce96d0f7da8bf1651c0a2e6
verified:
- by: process:claude-code-integration-phase0
  at: '2026-09-29T04:30:00Z'
  notes_sha256: 9469f61f318d2fb0871f23aed6c62eedb90c39d4811dc8c723af165ef60ba35c
  sources_sha256: a7fb3056b1f349861bc302e97cb8f880ccd73a1cfce96d0f7da8bf1651c0a2e6
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

* [application.ports.UnitOfWork](/symbols/application/ports/UnitOfWork.md) - All mutations on this port commit together or roll back together.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.policy.ensure_policy](/symbols/domain/policy/ensure_policy.md) - `def ensure_policy(model: Workflow, pack: Pack | None=None) -> None` in `domain/policy`.

## Referenced by

* [application.service.Studio.reset_preview](/symbols/application/service/Studio.reset_preview.md) - `def reset_preview(self, case_id: str, expected: int, state: str | None=None) -> dict[str, Any]` in `application/service`.
<!-- okf:generated:end links -->
