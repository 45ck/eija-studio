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
  sha256: 2326f02a459d9df3471e986a8133c5c8aa631bdb78a6dab44adb566771b49f31
notes_baseline: 8bc47825fdd7490cb764652bcc0f93045152e2eb3c9d5dbb2e2ded1c67b9b5be
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
* [`adapters/repository`](/modules/adapters/repository.md)
* [`adapters/self_facts`](/modules/adapters/self_facts.md)
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
* [adapters.repository](/modules/adapters/repository.md) - Repository analysis and bounded source navigation over captured checkout bytes.
* [adapters.self_facts](/modules/adapters/self_facts.md) - Syntactic facts about EIJA's own review implementation, never a conformance proof.
* [adapters.sqlite_store](/modules/adapters/sqlite_store.md) - Durable local unit of work.
* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [interfaces.cli](/modules/interfaces/cli.md) - Module `interfaces/cli` (no module docstring).
<!-- okf:generated:end links -->
