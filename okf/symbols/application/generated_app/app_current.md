---
type: Function
title: application.generated_app.app_current
description: Remeasure a selected application's current bytes through the existing port.
resource: repo://src/eija_studio/application/generated_app.py#app_current
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/generated_app.py#app_current
  title: application/generated_app.py
  hash_method: ast-v2
  sha256: 6862d0ba78fea3197da026148d64f31355c6d2a64bd78ca972579745978ef8ef
notes_baseline: 32d30846535a7b0644ba8defd23280c7d4f27950606172074083a9c8290d9246
---

# application.generated_app.app_current

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/generated_app`](/modules/application/generated_app.md) |
| Signature | `def app_current(case: ChangeCase, pack: Pack, apps: GeneratedApps \| None, identity_provider: IdentityProvider) -> dict[str, Any] \| None` |
| Code | `repo://src/eija_studio/application/generated_app.py#app_current` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Remeasure a selected application's current bytes through the existing port.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.ports.GeneratedApps](/symbols/application/ports/GeneratedApps.md) - Capture exact generated artifacts and observe the existing local conformance checker.
* [application.ports.IdentityProvider](/symbols/application/ports/IdentityProvider.md) - Type alias `IdentityProvider` in `application/ports`.
* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
