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
  sha256: 532c19a7ce9d38be1a1b2a8e7fbd602d1e7780bf085d9740a2fc0e0208dec26a
description_override: Seals a local-owner acknowledgement of the exact subject after eligibility, matching subject hash, acknowledged unknowns and correct answers.
notes_baseline: 68c33ff84805199a4305d2ea1a164289c7b961c89f51e2077022de24f1ab006f
verified:
- by: process:claude-code-integration-phase0
  at: '2026-09-29T04:30:00Z'
  notes_sha256: ba937fc8341dae9b8cbe5125142ef8b9e647472b12d1456ac0835ee3269a0879
  sources_sha256: 7264410159eb2ed16e2583b0f1a8cfa3a7db072c2b1f0632d96f3f8d16be94ee
- by: process:eija-wbs-1.3-agent
  at: '2026-09-29T08:20:47Z'
  notes_sha256: ba937fc8341dae9b8cbe5125142ef8b9e647472b12d1456ac0835ee3269a0879
  sources_sha256: 36d43f6f3d12babe5c5c57ea7c3d341c45adc9a1b656066dfd5496532bbca46c
- by: process:codex-ide-integration
  at: '2026-10-02T05:15:30Z'
  notes_sha256: ba937fc8341dae9b8cbe5125142ef8b9e647472b12d1456ac0835ee3269a0879
  sources_sha256: 08042ad0509f355fc844bba7a1c790b1d1eb25fc1d7e1b7ae918593254215b17
- by: process:playide-activation
  at: '2026-10-10T14:05:00+11:00'
  notes_sha256: edf767c3e0a57b0ed2a8819e020a00a274b93e6dce2a8808e61f0299b67a3ca7
  sources_sha256: e2c886fea320a5dcb43a27f3f73a6c607533e7406a3fc565c1108f825bd87e0a
- by: process:playide-activation
  at: '2026-10-10T02:55:29+00:00'
  notes_sha256: edf767c3e0a57b0ed2a8819e020a00a274b93e6dce2a8808e61f0299b67a3ca7
  sources_sha256: e2c886fea320a5dcb43a27f3f73a6c607533e7406a3fc565c1108f825bd87e0a
- by: process:playide-activation
  at: '2026-10-10T03:16:54Z'
  notes_sha256: 7bc5f5e1f1cd406e1c54f04ec080af6376b94d55aba2f4e9d83548cb50e11ddc
  sources_sha256: 68c33ff84805199a4305d2ea1a164289c7b961c89f51e2077022de24f1ab006f
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

Protected selection and history replay must agree with the candidate before a
decision is written. Reported step authorship does not authenticate the approving
owner, and invalid history never becomes an approval through candidate identity alone.

An already ineligible packet reports its policy/evidence refusal before replay;
eligible packets must pass replay before subject checks or decision writes.

<!-- okf:generated:begin links -->
## Depends on

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],…` in `application/compiler`.
* [application.history.replay](/symbols/application/history/replay.md) - Fail closed when stored commands no longer explain the candidate under the exact active pack.
* [application.service.now](/symbols/application/service/now.md) - `def now() -> str` in `application/service`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Principal](/symbols/domain/models/Principal.md) - `class Principal(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
