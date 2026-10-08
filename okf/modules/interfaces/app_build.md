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
  sha256: 30d1ea28aabfe7316b66e08b623f719a881b3b6017e6618fce0f15152306d486
notes_baseline: b9fc69c8fdaa11b91555ff6dddb034f29662c119bbee8374f028dd3316a1fc36
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
* [`bootstrap`](/modules/bootstrap.md)
* [`domain/models`](/modules/domain/models.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.appgen](/modules/application/appgen.md) - App generation: a reviewed workflow model becomes the spec and the conformance oracle of a runnable app (ADR-0150).
* [bootstrap](/modules/bootstrap.md) - The only composition root: wires application ports to concrete adapters.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).

## Referenced by

* [interfaces.cli](/modules/interfaces/cli.md) - Module `interfaces/cli` (no module docstring).
<!-- okf:generated:end links -->
