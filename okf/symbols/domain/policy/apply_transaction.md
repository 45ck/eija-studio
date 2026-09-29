---
type: Function
title: domain.policy.apply_transaction
description: Applies one typed SemanticTransaction to a policy-valid workflow and returns a candidate that is itself re-checked against the policy.
resource: repo://src/eija_studio/domain/policy.py#apply_transaction
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#apply_transaction
  title: domain/policy.py
  hash_method: ast-v2
  sha256: a374b6656c4d043e5ddf93667bde7dbc01e094078a3ac5fa55865483f9f4dc75
description_override: Applies one typed SemanticTransaction to a policy-valid workflow and returns a candidate that is itself re-checked against the policy.
notes_baseline: a6499ed96a231bd6a329a5e2f41416f28a97f2271588d97b4bb5c744b372d3db
---

# domain.policy.apply_transaction

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def apply_transaction(model: Workflow, tx: SemanticTransaction) -> Workflow` |
| Code | `repo://src/eija_studio/domain/policy.py#apply_transaction` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

The only path by which a meaning becomes a model. Policy is enforced on both sides: the input model must pass [ensure_policy](/symbols/domain/policy/ensure_policy.md), and so must the result.

* `enable_recommendation` adds `Recommend` (Teacher, `Submitted` to `Recommended`) and moves `Approve` to start from `Recommended`.
* `set_rejection_source` needs recommendation to be enabled first (`MEANING_REQUIRED`); it changes only where `Reject` starts (`Submitted` or `Recommended`).
* The result is rebuilt with [transition](/symbols/domain/policy/transition.md), so guards and effects always come from the protected tables and can never be supplied by the transaction.

Providers and agents never call it: authority to select a [Meaning](/language/meaning-selection.md) belongs to the local owner ([Studio.select](/symbols/application/service/Studio.select.md), [Studio.edit](/symbols/application/service/Studio.edit.md)).

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.SemanticTransaction](/symbols/domain/models/SemanticTransaction.md) - `class SemanticTransaction(Contract)` in `domain/models`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.policy.ensure_policy](/symbols/domain/policy/ensure_policy.md) - `def ensure_policy(model: Workflow) -> None` in `domain/policy`.
* [domain.policy.transition](/symbols/domain/policy/transition.md) - `def transition(action: str, source: str, target: str, role: str) -> Transition` in `domain/policy`.

## Referenced by

* [application.service.Studio.edit](/symbols/application/service/Studio.edit.md) - `def edit(self, case_id: str, expected: int, tx: SemanticTransaction, principal: Principal) -> dict` in `application/service`.
* [application.service.Studio.select](/symbols/application/service/Studio.select.md) - `def select(self, case_id: str, expected: int, interpretation: str, principal: Principal) -> dict` in `application/service`.
<!-- okf:generated:end links -->
