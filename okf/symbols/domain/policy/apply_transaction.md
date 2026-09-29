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
  sha256: 7e43b6e39e10fc04e88c8c609f3918bf23da0a70ba93bfd80b3b65de8b90678c
description_override: Applies one typed SemanticTransaction to a policy-valid workflow and returns a candidate that is itself re-checked against the policy.
notes_baseline: a6499ed96a231bd6a329a5e2f41416f28a97f2271588d97b4bb5c744b372d3db
---

# domain.policy.apply_transaction

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def apply_transaction(model: Workflow, tx: SemanticTransaction, pack: Pack \| None=None) -> Workflow` |
| Code | `repo://src/eija_studio/domain/policy.py#apply_transaction` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Legacy closed vocabulary (two kinds), kept until the open vocabulary of WBS 1.3 replaces it: the recommendation
meaning of the default pack and a rejection-source edit.
~~~
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
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.policy.ensure_policy](/symbols/domain/policy/ensure_policy.md) - `def ensure_policy(model: Workflow, pack: Pack | None=None) -> None` in `domain/policy`.
* [domain.policy.transition](/symbols/domain/policy/transition.md) - A transition for a declared action, with the action's declared guards and effects and the pack's forbidden effects.

## Referenced by

* [application.diagram_catalog.demo_pair](/symbols/application/diagram_catalog/demo_pair.md) - Baseline and the recommend_only candidate the excursion demo produces (rejection source Recommended).
* [application.formal.what_if_model](/symbols/application/formal/what_if_model.md) - The workflow an unsupported interpretation would produce (recommendation enabled, the fault applied), or None.
* [application.service.Studio.edit](/symbols/application/service/Studio.edit.md) - `def edit(self, case_id: str, expected: int, tx: SemanticTransaction, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.select](/symbols/application/service/Studio.select.md) - `def select(self, case_id: str, expected: int, interpretation: str, principal: Principal) -> dict[str, Any]` in `application/service`.
<!-- okf:generated:end links -->
