---
type: Function
title: domain.transactions.parse_transaction
description: Validate one transaction document; a malformed one is ``EDIT_INVALID``, never a crash.
resource: repo://src/eija_studio/domain/transactions.py#parse_transaction
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/transactions.py#parse_transaction
  title: domain/transactions.py
  hash_method: ast-v2
  sha256: 0c9a621bd44f274c1c9d3d92ebe36c3e4e3e77c0d5b316ea7ff60533685797a0
notes_baseline: 1976ca2e1e347e7db64a08f0ef26a5e6487a72605eb6366dcb59497dd8f59f81
---

# domain.transactions.parse_transaction

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/transactions`](/modules/domain/transactions.md) |
| Signature | `def parse_transaction(data: Any) -> Transaction` |
| Code | `repo://src/eija_studio/domain/transactions.py#parse_transaction` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Validate one transaction document; a malformed one is ``EDIT_INVALID``, never a crash.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.transactions.TRANSACTION_KINDS](/symbols/domain/transactions/TRANSACTION_KINDS.md) - Constant `TRANSACTION_KINDS` in `domain/transactions`.
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.
* [domain.transactions.TransactionDocument](/symbols/domain/transactions/TransactionDocument.md) - One semantic transaction as a JSON document (contracts/semantic-transaction.schema.json).

## Referenced by

* [application.edit_proposal.propose_edit](/symbols/application/edit_proposal/propose_edit.md) - No persistence or evidence: resolve one request, then use the existing policy-checked projection.
* [application.ripple.check_follow_ons](/symbols/application/ripple/check_follow_ons.md) - The proposer's follow-on steps, each re-checked on its own on top of the plan: a state-machine step through the policy (`base` with `plan` and the step), a scr…
<!-- okf:generated:end links -->
