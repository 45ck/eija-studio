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
  sha256: ff1db8f8ee923943861391b390dd6d8f6ccca65ea182f364587c3bdca7ce539a
notes_baseline: e8fd3031747a0b6ba71cf1cb9ed4288fdfd1d595edf62b2cd638fa1824e56e9b
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
