---
type: Function
title: domain.transactions.refused
description: '`def refused(code: str, message: str, *refs: str) -> DomainError` in `domain/transactions`.'
resource: repo://src/eija_studio/domain/transactions.py#refused
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/transactions.py#refused
  title: domain/transactions.py
  hash_method: ast-v2
  sha256: 442e5981ad175161e23a4482fda5c51edaadb665656bf2dc30ad2cf3201c222a
notes_baseline: 914d574380d8c94638a8c9862ee27f8dd1eb2b267d9155f35968d7aa5f71cf08
---

# domain.transactions.refused

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/transactions`](/modules/domain/transactions.md) |
| Signature | `def refused(code: str, message: str, *refs: str) -> DomainError` |
| Code | `repo://src/eija_studio/domain/transactions.py#refused` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.

## Referenced by

* [domain.transactions.apply_structural](/symbols/domain/transactions/apply_structural.md) - ``model`` with ``tx`` applied.
<!-- okf:generated:end links -->
