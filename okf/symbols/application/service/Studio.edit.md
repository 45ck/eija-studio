---
type: Method
title: application.service.Studio.edit
description: '`def edit(self, case_id: str, expected: int, tx: Transaction, principal: Principal) -> dict[str, Any]` in `application/service`.'
resource: repo://src/eija_studio/application/service.py#Studio.edit
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.edit
  title: application/service.py
  hash_method: ast-v2
  sha256: e0a9124b72205175e2a17262edb76e189d36cdc9ab49b1e08a5658cbb5831293
notes_baseline: 1882bffd1e414ae3f9b891f75cce6dd5e27e1de6e51c4a746a2bd72311619af0
---

# application.service.Studio.edit

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def edit(self, case_id: str, expected: int, tx: Transaction, principal: Principal) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service.py#Studio.edit` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.history.replay](/symbols/application/history/replay.md) - Fail closed when stored commands no longer explain the candidate under the exact active pack.
* [domain.models.Principal](/symbols/domain/models/Principal.md) - `class Principal(Contract)` in `domain/models`.
* [domain.policy.apply_transaction](/symbols/domain/policy/apply_transaction.md) - Apply one transaction (policy-checked).
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.
<!-- okf:generated:end links -->
