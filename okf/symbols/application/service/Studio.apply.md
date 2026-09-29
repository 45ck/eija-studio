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
  hash_method: ast-v2
  sha256: 9c9af5c81feca0582ccd012df03b49bb7497977805f6a11f59db9c087047957b
description_override: Applies an approved candidate to the local baseline only if an eligible, authentic, exact-subject decision exists.
notes_baseline: 43b77a6040925f386b0ccd8b5924d0609b2e34ba29a20b9cb683ae28a2501452
---

# application.service.Studio.apply

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def apply(self, case_id: str, expected: int, principal: Principal) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service.py#Studio.apply` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Requires `apply` and re-computes the packet at commit time. A changed active baseline adds the `STALE_BASELINE` blocker and the gate refuses; there is no automatic rebase (acceptance [AC06](/requirements/ac06.md)).

<!-- okf:generated:begin links -->
## Depends on

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],…` in `application/compiler`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Principal](/symbols/domain/models/Principal.md) - `class Principal(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
