---
type: Constant
title: domain.transactions.TRANSACTION_KINDS
description: Constant `TRANSACTION_KINDS` in `domain/transactions`.
resource: repo://src/eija_studio/domain/transactions.py#TRANSACTION_KINDS
tags:
- symbol
- domain
- constant
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/transactions.py#TRANSACTION_KINDS
  title: domain/transactions.py
  hash_method: ast-v2
  sha256: 0b00e90640417e539453f626558603bc9a4adfc43efc502fb524a4df80f80b7d
notes_baseline: b3a0987b433c44089f32d7ce7c0a4c681be87e935423d5a19171d0299a44c9cc
---

# domain.transactions.TRANSACTION_KINDS

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`domain/transactions`](/modules/domain/transactions.md) |
| Signature | `TRANSACTION_KINDS = ('add_state', 'rename_state', 'remove_state', 'set_initial', 'add_transition', 'retarget_transition', 'remove_transition', 'set_role', 'set…` |
| Code | `repo://src/eija_studio/domain/transactions.py#TRANSACTION_KINDS` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [domain.transactions.parse_transaction](/symbols/domain/transactions/parse_transaction.md) - Validate one transaction document; a malformed one is ``EDIT_INVALID``, never a crash.
<!-- okf:generated:end links -->
