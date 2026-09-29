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
  hash_method: ast-v2
  sha256: 6af8efea6c1f5cef2fd4499fc6f1497020e2d422bb12eff8040185f669ae231d
description_override: Seals a local-owner acknowledgement of the exact subject after eligibility, matching subject hash, acknowledged unknowns and correct answers.
notes_baseline: 0dd08f9d302d891992e32ff8449d0cd495edb04086ece4fa90528f747fdd53c7
---

# application.service.Studio.approve

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def approve(self, case_id: str, expected: int, subject_hash: str, answers: dict[str, str], acknowledge_unknowns: bool, principal: Principal, scope: str='local-demo') -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service.py#Studio.approve` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Requires `approve`. It is technical eligibility plus an explicit local acknowledgement, kept separate from apply; the sealed decision records `human_understanding: UNKNOWN` ([Local Decision](/language/local-decision.md)).

<!-- okf:generated:begin links -->
## Depends on

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],…` in `application/compiler`.
* [application.service.now](/symbols/application/service/now.md) - `def now() -> str` in `application/service`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Principal](/symbols/domain/models/Principal.md) - `class Principal(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
