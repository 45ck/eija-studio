---
type: Function
title: domain.transactions.element_refs
description: The model elements a transaction names (for refusal details).
resource: repo://src/eija_studio/domain/transactions.py#element_refs
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/transactions.py#element_refs
  title: domain/transactions.py
  hash_method: ast-v2
  sha256: 81c945ded4c3881f8e4a1e9f62ae5fa27280d839cf7c47cdfd143bde9e1764b4
notes_baseline: dea35a35a7f50d13e4f29f5e8ef674364549d6edaa292db424c9e6f5dda48265
---

# domain.transactions.element_refs

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/transactions`](/modules/domain/transactions.md) |
| Signature | `def element_refs(tx: Transaction) -> tuple[str, ...]` |
| Code | `repo://src/eija_studio/domain/transactions.py#element_refs` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The model elements a transaction names (for refusal details).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.

## Referenced by

* [domain.transactions.apply_structural](/symbols/domain/transactions/apply_structural.md) - ``model`` with ``tx`` applied.
<!-- okf:generated:end links -->
