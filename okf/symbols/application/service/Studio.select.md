---
type: Method
title: application.service.Studio.select
description: Records the owner's explicit choice of one supported interpretation and derives the candidate workflow.
resource: repo://src/eija_studio/application/service.py#Studio.select
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.select
  title: application/service.py
  hash_method: ast-v2
  sha256: 7884aba375c306bef2f6a0b867eed8473432e57ac89118516cb87b56cfda1e30
description_override: Records the owner's explicit choice of one supported interpretation and derives the candidate workflow.
notes_baseline: 94b71cd4e9f2946193b8bc0c926ce7b9f9d1d17f61f4afee9b26b7b2b1461de5
---

# application.service.Studio.select

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def select(self, case_id: str, expected: int, interpretation: str, principal: Principal) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service.py#Studio.select` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Requires the `select` capability. Only `recommend_only` is supported; other interpretations fail with `MEANING_UNSUPPORTED`. The candidate comes from [apply_transaction](/symbols/domain/policy/apply_transaction.md).

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Principal](/symbols/domain/models/Principal.md) - `class Principal(Contract)` in `domain/models`.
* [domain.models.SemanticTransaction](/symbols/domain/models/SemanticTransaction.md) - `class SemanticTransaction(Contract)` in `domain/models`.
* [domain.policy.CANONICAL_OPTIONS](/symbols/domain/policy/CANONICAL_OPTIONS.md) - Constant `CANONICAL_OPTIONS` in `domain/policy`.
* [domain.policy.apply_transaction](/symbols/domain/policy/apply_transaction.md) - `def apply_transaction(model: Workflow, tx: SemanticTransaction) -> Workflow` in `domain/policy`.
<!-- okf:generated:end links -->
