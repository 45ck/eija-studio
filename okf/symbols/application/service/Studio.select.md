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
  hash_method: ast-v1
  sha256: faf2984c2b9a0a933cdd2911fc9f6e10e226b31e72523e3a2d0b814eeb911dec
description_override: Records the owner's explicit choice of one supported interpretation and derives the candidate workflow.
---

# application.service.Studio.select

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def select(self, case_id: str, expected: int, interpretation: str, principal: Principal) -> dict` |
| Code | `repo://src/eija_studio/application/service.py#Studio.select` |
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Requires the `select` capability. Only `recommend_only` is supported; other interpretations fail with `MEANING_UNSUPPORTED`. The candidate comes from [apply_transaction](/symbols/domain/policy/apply_transaction.md).

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Principal](/symbols/domain/models/Principal.md) - `class Principal(Contract)` in `domain/models` (the source has no docstring).
* [domain.models.SemanticTransaction](/symbols/domain/models/SemanticTransaction.md) - `class SemanticTransaction(Contract)` in `domain/models` (the source has no docstring).
* [domain.policy.CANONICAL_OPTIONS](/symbols/domain/policy/CANONICAL_OPTIONS.md) - `CANONICAL_OPTIONS = {'recommend_only': {'label': 'Teacher recommends; registrar decides', 'supported': True, 'consequences': ['Only active, assigned…` in `dom…
* [domain.policy.apply_transaction](/symbols/domain/policy/apply_transaction.md) - `def apply_transaction(model: Workflow, tx: SemanticTransaction) -> Workflow` in `domain/policy` (the source has no docstring).
<!-- okf:generated:end links -->
