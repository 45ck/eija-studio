---
type: Function
title: domain.policy.ensure_policy
description: Raises DomainError POLICY_BLOCKED when check_policy reports any finding; called before every model is executed or transformed.
resource: repo://src/eija_studio/domain/policy.py#ensure_policy
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#ensure_policy
  title: domain/policy.py
  hash_method: ast-v1
  sha256: d50532d5168a83c6bdfac285bfeac9cea0fd26c84358da25b2a6c526a8d8e229
description_override: Raises DomainError POLICY_BLOCKED when check_policy reports any finding; called before every model is executed or transformed.
---

# domain.policy.ensure_policy

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def ensure_policy(model: Workflow) -> None` |
| Code | `repo://src/eija_studio/domain/policy.py#ensure_policy` |
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

The fail-closed wrapper: [runtime.execute](/symbols/application/runtime/execute.md), [runtime.initialise](/symbols/application/runtime/initialise.md) and [apply_transaction](/symbols/domain/policy/apply_transaction.md) all call it first, so an out-of-policy model cannot be previewed or run even if a caller skipped verification. The message lists the sorted finding codes from [check_policy](/symbols/domain/policy/check_policy.md).

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models` (the source has no docstring).
* [domain.policy.check_policy](/symbols/domain/policy/check_policy.md) - `def check_policy(model: Workflow) -> list[str]` in `domain/policy` (the source has no docstring).

## Referenced by

* [application.runtime.execute](/symbols/application/runtime/execute.md) - `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault=None) -> dict` in `application/runtime` (the source has no d…
* [application.runtime.initialise](/symbols/application/runtime/initialise.md) - `def initialise(session: UnitOfWork, case_id: str, model: Workflow, *, state: str | None=None) -> dict` in `application/runtime` (the source has no docstring).
* [domain.policy.apply_transaction](/symbols/domain/policy/apply_transaction.md) - `def apply_transaction(model: Workflow, tx: SemanticTransaction) -> Workflow` in `domain/policy` (the source has no docstring).
<!-- okf:generated:end links -->
