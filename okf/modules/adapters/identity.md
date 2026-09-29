---
type: Module
title: adapters.identity
description: Measured release identity, not a proof of correctness or author authenticity.
resource: repo://src/eija_studio/adapters/identity.py
tags:
- module
- adapters
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/adapters/identity.py
  title: adapters/identity.py
  hash_method: ast-api-v1
  sha256: 24cb598385954bb20629ea8b98200244c2509e49c5eabce08ba19b4d675fdf76
notes_baseline: da085560aa74af55315b7a2344be57f433ac0e03c02b2529a1dd00ab2fbc3fe5
---

# adapters.identity

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | adapters |
| Code | `repo://src/eija_studio/adapters/identity.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Measured release identity, not a proof of correctness or author authenticity.
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
