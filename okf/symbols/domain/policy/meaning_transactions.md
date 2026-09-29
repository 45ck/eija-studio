---
type: Function
title: domain.policy.meaning_transactions
description: '`def meaning_transactions(meaning_id: str, pack: Pack | None=None) -> tuple[Transaction, ...]` in `domain/policy`.'
resource: repo://src/eija_studio/domain/policy.py#meaning_transactions
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#meaning_transactions
  title: domain/policy.py
  hash_method: ast-v2
  sha256: 6bded7e27a373a0582d821a314539c90586553da803579aeec7232b9e2bfe544
notes_baseline: c63eceb67a48730babf121d8fb359503c75e469d4eee0df8ee427106b846144c
---

# domain.policy.meaning_transactions

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def meaning_transactions(meaning_id: str, pack: Pack \| None=None) -> tuple[Transaction, ...]` |
| Code | `repo://src/eija_studio/domain/policy.py#meaning_transactions` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.
<!-- okf:generated:end links -->
