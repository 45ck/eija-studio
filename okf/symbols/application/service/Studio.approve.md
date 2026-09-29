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
  sha256: 8002035a65ed8418dfa21983d8ab9f863040de38755ab1e380d510554fc377b8
description_override: Seals a local-owner acknowledgement of the exact subject after eligibility, matching subject hash, acknowledged unknowns and correct answers.
notes_baseline: 36d43f6f3d12babe5c5c57ea7c3d341c45adc9a1b656066dfd5496532bbca46c
verified:
- by: process:claude-code-integration-phase0
  at: '2026-09-29T04:30:00Z'
  notes_sha256: ba937fc8341dae9b8cbe5125142ef8b9e647472b12d1456ac0835ee3269a0879
  sources_sha256: 7264410159eb2ed16e2583b0f1a8cfa3a7db072c2b1f0632d96f3f8d16be94ee
- by: process:eija-wbs-1.3-agent
  at: '2026-09-29T08:20:47Z'
  notes_sha256: ba937fc8341dae9b8cbe5125142ef8b9e647472b12d1456ac0835ee3269a0879
  sources_sha256: 36d43f6f3d12babe5c5c57ea7c3d341c45adc9a1b656066dfd5496532bbca46c
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
