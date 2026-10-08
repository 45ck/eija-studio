---
type: Function
title: domain.policy.apply_structural_all
description: '``model`` with every transaction applied in order; structure only, no policy (what-if and meaning previews).'
resource: repo://src/eija_studio/domain/policy.py#apply_structural_all
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#apply_structural_all
  title: domain/policy.py
  hash_method: ast-v2
  sha256: 9c798e21b1a443135b06606005f47204e9eb122cf59795bd43a1e13a07314bd9
notes_baseline: 7ad6320e5d34b1fb25f6cb97fc0d32728ee6c07fee2f8448af746a3531338543
---

# domain.policy.apply_structural_all

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def apply_structural_all(model: Workflow, transactions: Sequence[Transaction], pack: Pack \| None=None) -> Workflow` |
| Code | `repo://src/eija_studio/domain/policy.py#apply_structural_all` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
``model`` with every transaction applied in order; structure only, no policy (what-if and meaning previews).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.
* [domain.transactions.apply_structural](/symbols/domain/transactions/apply_structural.md) - ``model`` with ``tx`` applied.

## Referenced by

* [domain.policy.apply_transactions](/symbols/domain/policy/apply_transactions.md) - Apply an edit sequence as one change: the start must conform, the result must conform (intermediate steps need only be coherent workflows).
* [domain.policy.what_if](/symbols/domain/policy/what_if.md) - What an UNSUPPORTED meaning would do to ``model`` (structure only, never a candidate), or None when it declares no transactions or they do not even apply struc…
<!-- okf:generated:end links -->
