---
type: Method
title: application.service.Studio.propose
description: Asks the configured provider for an untrusted interpretation and records the run; networked providers need startup enablement and explicit consent.
resource: repo://src/eija_studio/application/service.py#Studio.propose
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.propose
  title: application/service.py
  hash_method: ast-v2
  sha256: ec580383b5e6826564213f3a9a2ba73defc6e33a4c3ee76bb7186d031783972d
description_override: Asks the configured provider for an untrusted interpretation and records the run; networked providers need startup enablement and explicit consent.
notes_baseline: a88e6a4f634cb928096830759dec859aeb739d1cb0339ecea121bae9dc4d95d2
verified:
- by: process:claude-code-integration-phase0
  at: '2026-09-29T04:30:00Z'
  notes_sha256: 9eaed967eadbbad9e46e1dc21c81f14dd4ab9fab4ef1b40dd4b567b578051604
  sources_sha256: 5f16b9c69b6f03d1db68d7b7ae5194963849d2d8479a170b56dc0c83febfb927
- by: process:eija-wbs-1.3-agent
  at: '2026-09-29T08:20:47Z'
  notes_sha256: 9eaed967eadbbad9e46e1dc21c81f14dd4ab9fab4ef1b40dd4b567b578051604
  sources_sha256: c006c1563106547d851067d897263742b541cc8fceb4b67ed37f98766ef02a1b
- by: process:codex-ide-integration
  at: '2026-10-02T05:15:30Z'
  notes_sha256: 9eaed967eadbbad9e46e1dc21c81f14dd4ab9fab4ef1b40dd4b567b578051604
  sources_sha256: a88e6a4f634cb928096830759dec859aeb739d1cb0339ecea121bae9dc4d95d2
---

# application.service.Studio.propose

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def propose(self, case_id: str, expected: int, *, consent: bool=False) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service.py#Studio.propose` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

The provider call happens outside the database transaction, guarded by a single-flight lock; failure is audited with billing `UNKNOWN`. The proposal is stored but grants no authority.

<!-- okf:generated:begin links -->
## Depends on

* [application.service.now](/symbols/application/service/now.md) - `def now() -> str` in `application/service`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models`.
<!-- okf:generated:end links -->
