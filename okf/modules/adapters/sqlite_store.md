---
type: Module
title: adapters.sqlite_store
description: Durable local unit of work.
resource: repo://src/eija_studio/adapters/sqlite_store.py
tags:
- module
- adapters
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/adapters/sqlite_store.py
  title: adapters/sqlite_store.py
  hash_method: ast-api-v1
  sha256: fccde9123b884d8c6d3305baf9d40543a3e6c8b2b9c159a0a3e29f3b3885050e
notes_baseline: e8fcd735975240b69679413dfc9f2edeb283f6e21b5af0c74dd0fd2d1c92f34a
---

# adapters.sqlite_store

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | adapters |
| Code | `repo://src/eija_studio/adapters/sqlite_store.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Durable local unit of work. One database transaction owns state + operation + effects.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [bootstrap](/modules/bootstrap.md) - The only composition root: wires application ports to concrete adapters.
<!-- okf:generated:end links -->
