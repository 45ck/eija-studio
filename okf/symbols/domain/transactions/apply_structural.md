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
  sha256: 3f579211d8b45d63b882863c32ade3987d75a03f01df9ed7672402981af663ad
notes_baseline: b39a4a9964b7adcff2efeaf48d74a657f8df80b2275de3a903c530fa0cf59ac0
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
