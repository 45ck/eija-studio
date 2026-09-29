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
  sha256: f041dea781b0b1d4dcb5994d940268729fddc03986e53a2237372e61ba3feefa
description_override: Records the owner's explicit choice of one supported interpretation and derives the candidate workflow.
notes_baseline: b12570aef7471be1139026e37de6b57c6777343bcd0542b4c514c00f2ec8c636
verified:
- by: process:claude-code-integration-phase0
  at: '2026-09-29T04:30:00Z'
  notes_sha256: 3fd1dacbb7883b756008624e1ebb726f609f24a346667396ac4be9cf24662511
  sources_sha256: 24503fadd70f4c9f51e66b9e8a8697fa6f0f3dc48588ca733c3e341e13381369
- by: process:eija-wbs-1.3-agent
  at: '2026-09-29T08:20:47Z'
  notes_sha256: e96b3f94594a8a3d47fafcb4fcfba728cf874e4c5bd6ea96d3242ac134e2032c
  sources_sha256: b12570aef7471be1139026e37de6b57c6777343bcd0542b4c514c00f2ec8c636
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

Requires the `select` capability. The interpretation must be one the proposal offered and a meaning the pack declares as supported; otherwise `INTERPRETATION_MISSING` or `MEANING_UNSUPPORTED`. The candidate is the pack meaning's own transactions applied by `policy.apply_transactions` (policy-checked before and after); the transactions are recorded on the case. A case written in the pre-pack vocabulary is refused with `CASE_SCHEMA_OLD`.

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Principal](/symbols/domain/models/Principal.md) - `class Principal(Contract)` in `domain/models`.
* [domain.policy.apply_transactions](/symbols/domain/policy/apply_transactions.md) - Apply an edit sequence as one change: the start must conform, the result must conform (intermediate steps need only be coherent workflows).
<!-- okf:generated:end links -->
