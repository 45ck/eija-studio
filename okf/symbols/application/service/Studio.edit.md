---
type: Method
title: application.service.Studio.edit
description: '`def edit(self, case_id: str, expected: int, tx: SemanticTransaction, principal: Principal) -> dict` in `application/service` (the source has no docstring).'
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
  hash_method: ast-v1
  sha256: 65ef11aa5d392e2914a1eba08c5492c401a578c9c2798baae7cc09d60d8585ec
---

# application.service.Studio.edit

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def edit(self, case_id: str, expected: int, tx: SemanticTransaction, principal: Principal) -> dict` |
| Code | `repo://src/eija_studio/application/service.py#Studio.edit` |
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Principal](/symbols/domain/models/Principal.md) - `class Principal(Contract)` in `domain/models` (the source has no docstring).
* [domain.models.SemanticTransaction](/symbols/domain/models/SemanticTransaction.md) - `class SemanticTransaction(Contract)` in `domain/models` (the source has no docstring).
* [domain.policy.apply_transaction](/symbols/domain/policy/apply_transaction.md) - `def apply_transaction(model: Workflow, tx: SemanticTransaction) -> Workflow` in `domain/policy` (the source has no docstring).
<!-- okf:generated:end links -->
