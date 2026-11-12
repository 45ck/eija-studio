---
type: Function
title: domain.transactions.apply_structural
description: '``model`` with ``tx`` applied.'
resource: repo://src/eija_studio/domain/transactions.py#apply_structural
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/transactions.py#apply_structural
  title: domain/transactions.py
  hash_method: ast-v2
  sha256: 95d85ea8daac85cea5c803e1bae6613b358009fe024f31bce5ecdc1648cf38c1
notes_baseline: 7dc55adf5a6729db236b058c7974b3da7cadb8bba0141b19410bd9fe93cdf729
---

# domain.transactions.apply_structural

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/transactions`](/modules/domain/transactions.md) |
| Signature | `def apply_structural(model: Workflow, tx: Transaction, declare: Declare) -> Workflow` |
| Code | `repo://src/eija_studio/domain/transactions.py#apply_structural` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
``model`` with ``tx`` applied. Structural defects (unknown element, incoherent result) are ``EDIT_INVALID``.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.transactions.Declare](/symbols/domain/transactions/Declare.md) - Type alias `Declare` in `domain/transactions`.
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.
* [domain.transactions.element_refs](/symbols/domain/transactions/element_refs.md) - The model elements a transaction names (for refusal details).
* [domain.transactions.refused](/symbols/domain/transactions/refused.md) - `def refused(code: str, message: str, *refs: str) -> DomainError` in `domain/transactions`.

## Referenced by

* [domain.policy.apply_structural_all](/symbols/domain/policy/apply_structural_all.md) - ``model`` with every transaction applied in order; structure only, no policy (what-if and meaning previews).
<!-- okf:generated:end links -->
