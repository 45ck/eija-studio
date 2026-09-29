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
  sha256: 4c3ea304a74de099b9a5f48ac5bd257f517a966c53af0d3328c613a6ea69b891
description_override: Asks the configured provider for an untrusted interpretation and records the run; networked providers need startup enablement and explicit consent.
notes_baseline: ebf9eb94269ceae96303676ef0cc188001cf6b237e44e4d49bf68fcba6a1a707
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
