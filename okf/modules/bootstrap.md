---
type: Module
title: bootstrap
description: 'The only composition root: wires application ports to concrete adapters.'
resource: repo://src/eija_studio/bootstrap.py
tags:
- module
- root
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/bootstrap.py
  title: bootstrap.py
  hash_method: ast-api-v1
  sha256: 38731b986e6b052d51ca2d1dce2f2e3d01bcecd3757b6e7fd7fdc885622492e3
notes_baseline: 5a08ac4b825acd3f4c97d07021eec9b46d5546a9e7e95f775b241e955377bffc
---

# bootstrap

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | root |
| Code | `repo://src/eija_studio/bootstrap.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
The only composition root: wires application ports to concrete adapters.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`adapters/identity`](/modules/adapters/identity.md)
* [`adapters/receipts`](/modules/adapters/receipts.md)
* [`adapters/sqlite_store`](/modules/adapters/sqlite_store.md)
* [`application/service`](/modules/application/service.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [adapters.identity](/modules/adapters/identity.md) - Measured release identity, not a proof of correctness or author authenticity.
* [adapters.receipts](/modules/adapters/receipts.md) - Local integrity seal.
* [adapters.sqlite_store](/modules/adapters/sqlite_store.md) - Durable local unit of work.
* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [interfaces.cli](/modules/interfaces/cli.md) - Module `interfaces/cli` (no module docstring).
<!-- okf:generated:end links -->
