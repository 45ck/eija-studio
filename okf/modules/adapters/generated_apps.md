---
type: Module
title: adapters.generated_apps
description: Retain exact selected app bytes and run their existing generated unittest checker locally.
resource: repo://src/eija_studio/adapters/generated_apps.py
tags:
- module
- adapters
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/adapters/generated_apps.py
  title: adapters/generated_apps.py
  hash_method: ast-api-v1
  sha256: 41452a0da6943e7251d260ff965fcc175d63d3f6f8fa0db54b717f1a5ab60e95
notes_baseline: e053c7bd0a14c8d21d974a6602de0aab9eef4b754c321befd658dd4e670988c8
---

# adapters.generated_apps

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | adapters |
| Code | `repo://src/eija_studio/adapters/generated_apps.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Retain exact selected app bytes and run their existing generated unittest checker locally.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`application/ports`](/modules/application/ports.md)
* [`domain/generated_app`](/modules/domain/generated_app.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.ports](/modules/application/ports.md) - Application-owned ports.
* [domain.generated_app](/modules/domain/generated_app.md) - Versioned exact generated-app selection and evidence contracts; no authority is implied by a hash.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [bootstrap](/modules/bootstrap.md) - The only composition root: wires application ports to concrete adapters.
<!-- okf:generated:end links -->
