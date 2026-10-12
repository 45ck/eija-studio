---
type: Module
title: domain.generated_app
description: Versioned exact generated-app selection and evidence contracts; no authority is implied by a hash.
resource: repo://src/eija_studio/domain/generated_app.py
tags:
- module
- domain
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/generated_app.py
  title: domain/generated_app.py
  hash_method: ast-api-v1
  sha256: c3354a3c26df3fc4760ad53879b7345aec75790f576db389a8d0638368f8d50d
notes_baseline: 910ebcb9b3b12b34bfb89e6bd2159a5e95cc29e1604095f7e469cd40ee577917
---

# domain.generated_app

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | domain |
| Code | `repo://src/eija_studio/domain/generated_app.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Versioned exact generated-app selection and evidence contracts; no authority is implied by a hash.
~~~

## Public symbols

* [`Digest`](/symbols/domain/generated_app/Digest.md) (type-alias) - no docstring
* [`GeneratedAppActivation`](/symbols/domain/generated_app/GeneratedAppActivation.md) (class) - no docstring
* [`GeneratedAppBinding`](/symbols/domain/generated_app/GeneratedAppBinding.md) (class) - no docstring
* [`GeneratedBuildSubject`](/symbols/domain/generated_app/GeneratedBuildSubject.md) (class) - no docstring
* [`GeneratedCheckConfiguration`](/symbols/domain/generated_app/GeneratedCheckConfiguration.md) (class) - no docstring
* [`GeneratedChecker`](/symbols/domain/generated_app/GeneratedChecker.md) (class) - no docstring
* [`generated_receipt_status`](/symbols/domain/generated_app/generated_receipt_status.md) (function) - Compute a scoped process observation, never trust its submitted status field.

## Internal imports

* [`domain/models`](/modules/domain/models.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).

## Referenced by

* [adapters.generated_apps](/modules/adapters/generated_apps.md) - Retain exact selected app bytes and run their existing generated unittest checker locally.
* [application.generated_app](/modules/application/generated_app.md) - Shared generation and exact-app evidence operations for the existing kernel and checker.
* [application.ports](/modules/application/ports.md) - Application-owned ports.
* [application.service_views](/modules/application/service_views.md) - Read-only Studio projections over the same case, pack and exact-app evidence.
* [domain.change_case](/modules/domain/change_case.md) - Module `domain/change_case` (no module docstring).
* [domain.generated_app.Digest](/symbols/domain/generated_app/Digest.md) - Type alias `Digest` in `domain/generated_app`.
* [domain.generated_app.GeneratedAppActivation](/symbols/domain/generated_app/GeneratedAppActivation.md) - `class GeneratedAppActivation(Contract)` in `domain/generated_app`.
* [domain.generated_app.GeneratedAppBinding.consistent_digest](/symbols/domain/generated_app/GeneratedAppBinding.consistent_digest.md) - `def consistent_digest(self) -> Self` in `domain/generated_app`.
* [domain.generated_app.GeneratedAppBinding](/symbols/domain/generated_app/GeneratedAppBinding.md) - `class GeneratedAppBinding(Contract)` in `domain/generated_app`.
* [domain.generated_app.GeneratedBuildSubject.consistent_digest](/symbols/domain/generated_app/GeneratedBuildSubject.consistent_digest.md) - `def consistent_digest(self) -> Self` in `domain/generated_app`.
* [domain.generated_app.GeneratedBuildSubject](/symbols/domain/generated_app/GeneratedBuildSubject.md) - `class GeneratedBuildSubject(Contract)` in `domain/generated_app`.
* [domain.generated_app.GeneratedCheckConfiguration](/symbols/domain/generated_app/GeneratedCheckConfiguration.md) - `class GeneratedCheckConfiguration(Contract)` in `domain/generated_app`.
* [domain.generated_app.GeneratedChecker](/symbols/domain/generated_app/GeneratedChecker.md) - `class GeneratedChecker(Contract)` in `domain/generated_app`.
* [domain.generated_app.generated_receipt_status](/symbols/domain/generated_app/generated_receipt_status.md) - Compute a scoped process observation, never trust its submitted status field.
<!-- okf:generated:end links -->
