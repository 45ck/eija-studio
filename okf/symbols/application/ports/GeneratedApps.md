---
type: Class
title: application.ports.GeneratedApps
description: Capture exact generated artifacts and observe the existing local conformance checker.
resource: repo://src/eija_studio/application/ports.py#GeneratedApps
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/ports.py#GeneratedApps
  title: application/ports.py
  hash_method: ast-sig-v1
  sha256: c13a5f719d9ee5492f980dba763bce5d49fd34c04d803d1904c349725f4a69e9
notes_baseline: 7ac0536438db02225a8f9f85573d1962276b47d0e953deb76e49b0afbd057219
---

# application.ports.GeneratedApps

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/ports`](/modules/application/ports.md) |
| Signature | `class GeneratedApps(Protocol)` |
| Code | `repo://src/eija_studio/application/ports.py#GeneratedApps` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Capture exact generated artifacts and observe the existing local conformance checker.
~~~

## Protocol members

Structural interface implemented by adapters; not a class to instantiate.

* `def capture(self, pack: Pack, model: Workflow, expected_digest: str, identity_provider: IdentityProvider) -> GeneratedAppBinding`
* `def current(self, pack: Pack, model: Workflow, binding: GeneratedAppBinding, identity_provider: IdentityProvider) -> dict[str, Any]`
* `def verify(self, binding: GeneratedAppBinding, identity_provider: IdentityProvider) -> dict[str, Any]`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.ports.IdentityProvider](/symbols/application/ports/IdentityProvider.md) - Type alias `IdentityProvider` in `application/ports`.
* [domain.generated_app.GeneratedAppBinding](/symbols/domain/generated_app/GeneratedAppBinding.md) - `class GeneratedAppBinding(Contract)` in `domain/generated_app`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.generated_app.app_current](/symbols/application/generated_app/app_current.md) - Remeasure a selected application's current bytes through the existing port.
* [application.generated_app.capture_app](/symbols/application/generated_app/capture_app.md) - Bind the checked payload to this exact selected case; persistence stays in Studio.
* [application.generated_app.verify_app](/symbols/application/generated_app/verify_app.md) - Seal the observed checker artifact, without approving or writing the case.
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio(StudioViews)` in `application/service`.
<!-- okf:generated:end links -->
