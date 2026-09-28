---
type: Module
title: adapters.providers
description: Untrusted proposal adapters.
resource: repo://src/eija_studio/adapters/providers.py
tags:
- module
- adapters
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/adapters/providers.py
  title: adapters/providers.py
  hash_method: ast-api-v1
  sha256: 0fb311a39c77aec5ac5a32807cff2ce27c3dc6509fcee620468d1167504b4253
notes_baseline: 278502a583e7149fa59536dc10ef46740a49e37e1b03c3673758d35432199a11
---

# adapters.providers

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | adapters |
| Code | `repo://src/eija_studio/adapters/providers.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Untrusted proposal adapters. No implementation, evidence or governance tools are exposed.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`application/ports`](/modules/application/ports.md)
* [`domain/models`](/modules/domain/models.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.ports](/modules/application/ports.md) - Application-owned ports.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).

## Referenced by

* [Provider integration](/contexts/provider-integration.md) - Owns Vendor transport, authentication delegation, limits and response normalization
* [bootstrap](/modules/bootstrap.md) - The only composition root: wires application ports to concrete adapters.
<!-- okf:generated:end links -->
