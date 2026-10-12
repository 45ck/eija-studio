---
type: Module
title: interfaces.play_presentation
description: Read-only presentation inspection within PlayIDE's authenticated boundary.
resource: repo://src/eija_studio/interfaces/play_presentation.py
tags:
- module
- interfaces
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/interfaces/play_presentation.py
  title: interfaces/play_presentation.py
  hash_method: ast-api-v1
  sha256: ed8fc1e11a150f079ac4893278bb50c0d8d716320ca036c1f05b5bdd3e85480d
notes_baseline: d94329f49b157fab87ac68cc1f0a2a5fee7d28485da18cea46ff2129ab34cc5d
---

# interfaces.play_presentation

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | interfaces |
| Code | `repo://src/eija_studio/interfaces/play_presentation.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Read-only presentation inspection within PlayIDE's authenticated boundary.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`application/presentation`](/modules/application/presentation.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/screens`](/modules/domain/screens.md)
* [`interfaces/app_build`](/modules/interfaces/app_build.md)
* [`interfaces/c4`](/modules/interfaces/c4.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.presentation](/modules/application/presentation.md) - A bounded presentation/navigation lens over one exact generated snapshot.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.screens](/modules/domain/screens.md) - Screens: the user interface of a pack's app, designed against its use cases and data model (ADR-0154).
* [interfaces.app_build](/modules/interfaces/app_build.md) - `eija build`: write a runnable app generated from a pack's model, then run its kernel conformance tests (ADR-0150).
* [interfaces.c4](/modules/interfaces/c4.md) - C4 structural inspection under the existing authenticated PlayIDE boundary.

## Referenced by

* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
<!-- okf:generated:end links -->
