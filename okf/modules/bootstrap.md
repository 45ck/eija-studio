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
  sha256: a1127de2561670d3aa739bd220139ac386c5a813e5c75a802b1a992b34b57d71
notes_baseline: 32cdefd065afda773184b28d119ad238e45cf1865e5f9bf7af4b96968675de1a
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
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [adapters.identity](/modules/adapters/identity.md) - Measured release identity, not a proof of correctness or author authenticity.
* [adapters.receipts](/modules/adapters/receipts.md) - Local integrity seal.
* [adapters.sqlite_store](/modules/adapters/sqlite_store.md) - Durable local unit of work.
* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).

## Referenced by

* [interfaces.cli](/modules/interfaces/cli.md) - Module `interfaces/cli` (no module docstring).
<!-- okf:generated:end links -->
