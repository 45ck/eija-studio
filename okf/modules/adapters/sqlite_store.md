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
  sha256: 1fafc7e2fbffc499f563c857b4a359af6bf1319ba797138fa9757ed66cd59610
notes_baseline: 7dac192ed751f2c9df4f0540a073c071a3f75497f9d8b4cc294be535eb869c7e
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
