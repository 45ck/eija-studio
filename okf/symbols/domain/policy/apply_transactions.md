---
type: Function
title: domain.policy.apply_transactions
description: 'Apply an edit sequence as one change: the start must conform, the result must conform (intermediate steps need only be coherent workflows).'
resource: repo://src/eija_studio/domain/policy.py#apply_transactions
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#apply_transactions
  title: domain/policy.py
  hash_method: ast-v2
  sha256: 3aec735487317c86f18ec3263310ad6436dd3ea3a4c329c369299327196c4897
notes_baseline: b90c4f5f73c0705ab9f68cfbddfa86d6a9124aa6cd4b3b10df2303c2be09a3a1
---

# domain.policy.apply_transactions

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def apply_transactions(model: Workflow, transactions: Sequence[Transaction], pack: Pack \| None=None) -> Workflow` |
| Code | `repo://src/eija_studio/domain/policy.py#apply_transactions` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Apply an edit sequence as one change: the start must conform, the result must conform (intermediate steps
need only be coherent workflows). A refusal carries ``details`` {codes, refs} naming the laws it breaks.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.policy.apply_structural_all](/symbols/domain/policy/apply_structural_all.md) - ``model`` with every transaction applied in order; structure only, no policy (what-if and meaning previews).
* [domain.policy.ensure_policy](/symbols/domain/policy/ensure_policy.md) - `def ensure_policy(model: Workflow, pack: Pack | None=None) -> None` in `domain/policy`.
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.

## Referenced by

* [application.service.Studio.edit](/symbols/application/service/Studio.edit.md) - `def edit(self, case_id: str, expected: int, tx: Transaction, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.select](/symbols/application/service/Studio.select.md) - `def select(self, case_id: str, expected: int, interpretation: str, principal: Principal) -> dict[str, Any]` in `application/service`.
* [domain.affordance.dry_run](/symbols/domain/affordance/dry_run.md) - {legal, codes, refs} of applying ``tx`` to ``model`` under ``pack``, without applying it anywhere.
* [domain.policy.apply_meaning](/symbols/domain/policy/apply_meaning.md) - The candidate a supported pack meaning produces from ``model`` (policy-checked).
* [domain.policy.apply_transaction](/symbols/domain/policy/apply_transaction.md) - Apply one transaction (policy-checked).
<!-- okf:generated:end links -->
