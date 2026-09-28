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
  hash_method: ast-v1
  sha256: 6ec619cc697f83b6bd11b7429561f5beac22703e31d9d3e9b30bbf4f1a2c3f42
description_override: Asks the configured provider for an untrusted interpretation and records the run; networked providers need startup enablement and explicit consent.
---

# application.service.Studio.propose

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def propose(self, case_id: str, expected: int, *, consent=False) -> dict` |
| Code | `repo://src/eija_studio/application/service.py#Studio.propose` |
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

The provider call happens outside the database transaction, guarded by a single-flight lock; failure is audited with billing `UNKNOWN`. The proposal is stored but grants no authority.

<!-- okf:generated:begin links -->
## Depends on

* [application.service.now](/symbols/application/service/now.md) - `def now() -> str` in `application/service` (the source has no docstring).
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models` (the source has no docstring).
<!-- okf:generated:end links -->
