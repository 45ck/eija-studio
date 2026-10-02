---
type: Module
title: adapters.repository
description: Repository analysis and bounded source navigation over captured checkout bytes.
resource: repo://src/eija_studio/adapters/repository.py
tags:
- module
- adapters
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/adapters/repository.py
  title: adapters/repository.py
  hash_method: ast-api-v1
  sha256: d82e8a70eba3cb4dc2b3ddd1c260f16db9a4ce23c84667e035285f3656b5095a
notes_baseline: 0d5db1c2d7cb826ea7d749cfa6bca1fdac81ef41c934f41a2d91d72b5f3b03aa
---

# adapters.repository

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | adapters |
| Code | `repo://src/eija_studio/adapters/repository.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Repository analysis and bounded source navigation over captured checkout bytes.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`adapters/repository_capture`](/modules/adapters/repository_capture.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [adapters.repository_capture](/modules/adapters/repository_capture.md) - Bounded repository reads adapted to the existing deterministic Weave engine.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [bootstrap](/modules/bootstrap.md) - The only composition root: wires application ports to concrete adapters.
<!-- okf:generated:end links -->
