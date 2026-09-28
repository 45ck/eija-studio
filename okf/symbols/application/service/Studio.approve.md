---
type: Method
title: application.service.Studio.approve
description: Seals a local-owner acknowledgement of the exact subject after eligibility, matching subject hash, acknowledged unknowns and correct answers.
resource: repo://src/eija_studio/application/service.py#Studio.approve
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.approve
  title: application/service.py
  hash_method: ast-v1
  sha256: 8b414be6ede961c316513a0a70320314e42127bcb238ca92bc3c7d269020d0f6
description_override: Seals a local-owner acknowledgement of the exact subject after eligibility, matching subject hash, acknowledged unknowns and correct answers.
---

# application.service.Studio.approve

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def approve(self, case_id: str, expected: int, subject_hash: str, answers: dict[str, str], acknowledge_unknowns: bool, principal: Principal, scope: str='local-demo') -> dict` |
| Code | `repo://src/eija_studio/application/service.py#Studio.approve` |
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Requires `approve`. It is technical eligibility plus an explicit local acknowledgement, kept separate from apply; the sealed decision records `human_understanding: UNKNOWN` ([Local Decision](/language/local-decision.md)).

<!-- okf:generated:begin links -->
## Depends on

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict, authenticator, active_version: int, scope: str='local-demo') -> dict` in `application/compiler` (the source…
* [application.service.now](/symbols/application/service/now.md) - `def now() -> str` in `application/service` (the source has no docstring).
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Principal](/symbols/domain/models/Principal.md) - `class Principal(Contract)` in `domain/models` (the source has no docstring).
<!-- okf:generated:end links -->
