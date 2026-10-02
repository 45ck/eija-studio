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
  sha256: 2b1d1b0e39f3ac6384da2ed8922af411b422ff7cf9203abfcee44764639c1a37
description_override: Applies an approved candidate to the local baseline only if an eligible, authentic, exact-subject decision exists.
notes_baseline: f3fe728d004fdf9381dbdb0a3820463ff787d783299933a1d9f3a36bcb10f0a7
verified:
- by: process:claude-code-integration-phase0
  at: '2026-09-29T04:30:00Z'
  notes_sha256: 54d1699727ddc6215c45a311cfd5ca0d7b2baec089d1da3d52e339a74175fd64
  sources_sha256: 227e5a988200c87eff573195eafe8d2a5f3ff1712b64f8326495d8950a1911a3
- by: process:eija-wbs-1.3-agent
  at: '2026-09-29T08:20:47Z'
  notes_sha256: 54d1699727ddc6215c45a311cfd5ca0d7b2baec089d1da3d52e339a74175fd64
  sources_sha256: ca2a11fdbb4c4f097688f5edebe043fbdb79a703f796a996e98eda67fb3f7a0c
- by: process:codex-ide-integration
  at: '2026-10-02T05:15:30Z'
  notes_sha256: 54d1699727ddc6215c45a311cfd5ca0d7b2baec089d1da3d52e339a74175fd64
  sources_sha256: f3fe728d004fdf9381dbdb0a3820463ff787d783299933a1d9f3a36bcb10f0a7
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
