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
  sha256: 6f0b387ddd98bb5770067d0b6e311e70242637c192317ae8777ca2a250d04421
notes_baseline: 747a904209a9d032b29946b2f6e3d2f85bf1db91689360354e45080ffa875ad6
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
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.appgen](/modules/application/appgen.md) - App generation: a reviewed workflow model becomes a runnable app and its conformance oracle (ADR-0150).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [interfaces.cli](/modules/interfaces/cli.md) - Module `interfaces/cli` (no module docstring).
* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, and Build & run of the model as a live app beside it (ADR-0151).
<!-- okf:generated:end links -->
