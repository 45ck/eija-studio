---
type: Method
title: application.service.Studio.edit
description: '`def edit(self, case_id: str, expected: int, tx: SemanticTransaction, principal: Principal) -> dict[str, Any]` in `application/service`.'
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
  sha256: f65d8a0e20dca7d97db8df3c816f58195f09c80f0c938e5ef8beebd95f5dc6f5
notes_baseline: f7e30e771eecec0174d08d16f08f578c96546ffac5256af991f58bee60aaf8a2
---

# application.service.Studio.edit

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def edit(self, case_id: str, expected: int, tx: SemanticTransaction, principal: Principal) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service.py#Studio.edit` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Principal](/symbols/domain/models/Principal.md) - `class Principal(Contract)` in `domain/models`.
* [domain.models.SemanticTransaction](/symbols/domain/models/SemanticTransaction.md) - `class SemanticTransaction(Contract)` in `domain/models`.
* [domain.policy.apply_transaction](/symbols/domain/policy/apply_transaction.md) - `def apply_transaction(model: Workflow, tx: SemanticTransaction) -> Workflow` in `domain/policy`.
<!-- okf:generated:end links -->
