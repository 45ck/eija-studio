---
type: Function
title: application.generated_app.capture_app
description: Bind the checked payload to this exact selected case; persistence stays in Studio.
resource: repo://src/eija_studio/application/generated_app.py#capture_app
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/generated_app.py#capture_app
  title: application/generated_app.py
  hash_method: ast-v2
  sha256: 597bb124b2a6710f946f0e3f9a739683386002bf30603f001412336c2ace598f
notes_baseline: 7a7bfe58057435a30009aeb68d1080234d1787d11313a9541b904d10a2a1cfa7
---

# application.generated_app.capture_app

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/generated_app`](/modules/application/generated_app.md) |
| Signature | `def capture_app(case: ChangeCase, expected_digest: str, pack: Pack, apps: GeneratedApps \| None, identity_provider: IdentityProvider) -> tuple[ChangeCase, str]` |
| Code | `repo://src/eija_studio/application/generated_app.py#capture_app` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Bind the checked payload to this exact selected case; persistence stays in Studio.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.ports.GeneratedApps](/symbols/application/ports/GeneratedApps.md) - Capture exact generated artifacts and observe the existing local conformance checker.
* [application.ports.IdentityProvider](/symbols/application/ports/IdentityProvider.md) - Type alias `IdentityProvider` in `application/ports`.
* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.service.Studio.from_plan](/symbols/application/service/Studio.from_plan.md) - Select an exact owner-reviewed command batch; previews and provenance never grant authority.
<!-- okf:generated:end links -->
