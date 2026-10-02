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
  sha256: 4768634617fda3a8dbec19f5055778bb2d71968b1fdc8025da410fea248b852f
description_override: Applies one typed SemanticTransaction to a policy-valid workflow and returns a candidate that is itself re-checked against the policy.
notes_baseline: 0f924881e6afa2a9fbc58b0a10c619d04f0d70cb9e0bce8d6768a1813cca8318
verified:
- by: process:eija-wbs-1.3-agent
  at: '2026-09-29T08:20:47Z'
  notes_sha256: 087e615d318ca230268ebd8b8df30c420b1bc8be7156f6fc9922357da9c1500a
  sources_sha256: 0f924881e6afa2a9fbc58b0a10c619d04f0d70cb9e0bce8d6768a1813cca8318
---

# domain.policy.apply_transaction

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def apply_transaction(model: Workflow, tx: Transaction \| SemanticTransaction, pack: Pack \| None=None) -> Workflow` |
| Code | `repo://src/eija_studio/domain/policy.py#apply_transaction` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Apply one transaction (policy-checked). The deprecated ``SemanticTransaction`` (only
verification/bend/bend_generate.py still builds one; see models.py) means "the pack's first supported meaning".
~~~
<!-- okf:generated:end facts -->

## Notes

Applies one transaction of the open vocabulary through `apply_transactions`: the input model must pass [ensure_policy](/symbols/domain/policy/ensure_policy.md), and so must the result. Structural defects are `EDIT_INVALID`; a policy refusal is `POLICY_BLOCKED` with `details {codes, refs}` naming the laws broken.
* An added transition takes its guards and effects from the pack's declared action, so a transaction never supplies its own guards or effects to an added transition; `set_guards`/`set_effects` are judged by the policy like any other edit.
* The deprecated [SemanticTransaction](/symbols/domain/models/SemanticTransaction.md) means the pack's first supported meaning.

Providers and agents never call it: authority to select a [Meaning](/language/meaning-selection.md) or edit belongs to the local owner ([Studio.select](/symbols/application/service/Studio.select.md), [Studio.edit](/symbols/application/service/Studio.edit.md)).

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.SemanticTransaction](/symbols/domain/models/SemanticTransaction.md) - DEPRECATED closed vocabulary, superseded by the open one in ``domain.transactions`` (WBS 1.3).
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.policy.apply_meaning](/symbols/domain/policy/apply_meaning.md) - The candidate a supported pack meaning produces from ``model`` (policy-checked).
* [domain.policy.apply_transactions](/symbols/domain/policy/apply_transactions.md) - Apply an edit sequence as one change: the start must conform, the result must conform (intermediate steps need only be coherent workflows).
* [domain.policy.first_supported_meaning](/symbols/domain/policy/first_supported_meaning.md) - The id of the pack's first supported meaning (the demo candidate's meaning).
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.

## Referenced by

* [application.service.Studio.edit](/symbols/application/service/Studio.edit.md) - `def edit(self, case_id: str, expected: int, tx: Transaction, principal: Principal) -> dict[str, Any]` in `application/service`.
<!-- okf:generated:end links -->
