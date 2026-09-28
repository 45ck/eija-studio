---
type: Method
title: application.service.Studio.apply
description: Applies an approved candidate to the local baseline only if an eligible, authentic, exact-subject decision exists.
resource: repo://src/eija_studio/application/service.py#Studio.apply
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.apply
  title: application/service.py
  hash_method: ast-v1
  sha256: 0a310f8bb8f5eac5cfb1600aa191333072be7078c1b64dee442469e7abd4c13e
description_override: Applies an approved candidate to the local baseline only if an eligible, authentic, exact-subject decision exists.
---

# application.service.Studio.apply

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def apply(self, case_id: str, expected: int, principal: Principal) -> dict` |
| Code | `repo://src/eija_studio/application/service.py#Studio.apply` |
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Requires `apply` and re-computes the packet at commit time. A changed active baseline adds the `STALE_BASELINE` blocker and the gate refuses; there is no automatic rebase (acceptance [AC06](/requirements/ac06.md)).

<!-- okf:generated:begin links -->
## Depends on

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict, authenticator, active_version: int, scope: str='local-demo') -> dict` in `application/compiler` (the source…
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Principal](/symbols/domain/models/Principal.md) - `class Principal(Contract)` in `domain/models` (the source has no docstring).
<!-- okf:generated:end links -->
