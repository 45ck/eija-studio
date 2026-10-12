---
type: Module
title: interfaces.app_build
description: '`eija build`: write a runnable app generated from a pack''s model, then run its kernel conformance tests (ADR-0150).'
resource: repo://src/eija_studio/interfaces/app_build.py
tags:
- module
- interfaces
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/interfaces/app_build.py
  title: interfaces/app_build.py
  hash_method: ast-api-v1
  sha256: 1a0ce7792a64a2cd4e346ae908c00da53e43e3b7ec92d31336e992aff09bbdc0
notes_baseline: c812c435eec8dd664eda5a626fe54c73116c16899ce838bfcc3413199d0d0d93
---

# interfaces.app_build

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | interfaces |
| Code | `repo://src/eija_studio/interfaces/app_build.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
`eija build`: write a runnable app generated from a pack's model, then run its kernel conformance tests (ADR-0150).
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`application/appgen`](/modules/application/appgen.md)
* [`application/build_subject`](/modules/application/build_subject.md)
* [`application/generated_app`](/modules/application/generated_app.md)
* [`application/ports`](/modules/application/ports.md)
* [`domain/data`](/modules/domain/data.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/screens`](/modules/domain/screens.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.appgen](/modules/application/appgen.md) - App generation: a reviewed workflow model becomes a runnable app and its conformance oracle (ADR-0150).
* [application.build_subject](/modules/application/build_subject.md) - Exact generated-build identity.
* [application.generated_app](/modules/application/generated_app.md) - Shared generation and exact-app evidence operations for the existing kernel and checker.
* [application.ports](/modules/application/ports.md) - Application-owned ports.
* [domain.data](/modules/domain/data.md) - The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.screens](/modules/domain/screens.md) - Screens: the user interface of a pack's app, designed against its use cases and data model (ADR-0154).

## Referenced by

* [interfaces.c4](/modules/interfaces/c4.md) - C4 structural inspection under the existing authenticated PlayIDE boundary.
* [interfaces.cli](/modules/interfaces/cli.md) - Module `interfaces/cli` (no module docstring).
* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
* [interfaces.play_presentation](/modules/interfaces/play_presentation.md) - Read-only presentation inspection within PlayIDE's authenticated boundary.
<!-- okf:generated:end links -->
