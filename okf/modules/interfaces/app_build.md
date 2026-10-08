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
  sha256: b9491b73b3e990edac84abe283b7202ee5ddcf4e7d07ead5138e33d15de8a977
notes_baseline: 871ea73bc112db2fccc6700006ba0e6c6bda441cdc9a5aa8487109518bc6302e
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

* [application.appgen](/modules/application/appgen.md) - App generation: a reviewed workflow model becomes the spec and the conformance oracle of a runnable app (ADR-0150).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [interfaces.cli](/modules/interfaces/cli.md) - Module `interfaces/cli` (no module docstring).
<!-- okf:generated:end links -->
