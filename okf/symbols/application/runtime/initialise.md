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
  hash_method: ast-v1
  sha256: 6c5f0957022fe1d4c1f5611b7bcc279f76b02975e90671a0ff9d465a65ce01cc
description_override: Creates an isolated preview instance bound to a model hash at version 0, after the policy check.
---

# application.runtime.initialise

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/runtime`](/modules/application/runtime.md) |
| Signature | `def initialise(session: UnitOfWork, case_id: str, model: Workflow, *, state: str \| None=None) -> dict` |
| Code | `repo://src/eija_studio/application/runtime.py#initialise` |
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

A changed candidate makes the instance stale; reset creates a new instance instead of migrating the old one ([Preview Instance](/language/preview-instance.md)).

<!-- okf:generated:begin links -->
## Depends on

* [application.ports.UnitOfWork](/symbols/application/ports/UnitOfWork.md) - All mutations on this port commit together or roll back together.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models` (the source has no docstring).
* [domain.policy.ensure_policy](/symbols/domain/policy/ensure_policy.md) - `def ensure_policy(model: Workflow) -> None` in `domain/policy` (the source has no docstring).

## Referenced by

* [application.service.Studio.reset_preview](/symbols/application/service/Studio.reset_preview.md) - `def reset_preview(self, case_id: str, expected: int, state: str | None=None) -> dict` in `application/service` (the source has no docstring).
* [application.verifier.verify_runtime](/symbols/application/verifier/verify_runtime.md) - `def verify_runtime(model: Workflow, subject: dict, sandbox: SandboxFactory) -> dict` in `application/verifier` (the source has no docstring).
<!-- okf:generated:end links -->
