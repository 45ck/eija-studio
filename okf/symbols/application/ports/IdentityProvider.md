---
type: Type Alias
title: application.ports.IdentityProvider
description: Type alias `IdentityProvider` in `application/ports`.
resource: repo://src/eija_studio/application/ports.py#IdentityProvider
tags:
- symbol
- application
- type-alias
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/ports.py#IdentityProvider
  title: application/ports.py
  hash_method: ast-v2
  sha256: 36975c2db982357100389061ba3b20ce6463ecc3a4b11b201ae1331e3a49660e
notes_baseline: 11b2561cd522b2123c645a90d9c8aab67ffc0139148e3b357148d27cd8790bbf
---

# application.ports.IdentityProvider

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | type-alias |
| Module | [`application/ports`](/modules/application/ports.md) |
| Signature | `IdentityProvider = Callable[[], dict[str, Any]]` |
| Code | `repo://src/eija_studio/application/ports.py#IdentityProvider` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [application.generated_app.app_current](/symbols/application/generated_app/app_current.md) - Remeasure a selected application's current bytes through the existing port.
* [application.generated_app.capture_app](/symbols/application/generated_app/capture_app.md) - Bind the checked payload to this exact selected case; persistence stays in Studio.
* [application.generated_app.verify_app](/symbols/application/generated_app/verify_app.md) - Seal the observed checker artifact, without approving or writing the case.
* [application.ports.GeneratedApps](/symbols/application/ports/GeneratedApps.md) - Capture exact generated artifacts and observe the existing local conformance checker.
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio(StudioViews)` in `application/service`.
* [application.service_views.StudioViews](/symbols/application/service_views/StudioViews.md) - Projection half of Studio; callbacks use the command service's case and review checks.
<!-- okf:generated:end links -->
