---
type: Method
title: application.service.Studio.edit
description: '`def edit(self, case_id: str, expected: int, tx: SemanticTransaction, principal: Principal) -> dict` in `application/service`.'
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
  sha256: c5dc1b92e323794964fdbf417794a8ff0b6d47797014fccb191145d31a9f2ec9
notes_baseline: ba05775e815c1fd83d45f0c756246672e3b6e1a252ae31850c9c0fc40245af6d
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
