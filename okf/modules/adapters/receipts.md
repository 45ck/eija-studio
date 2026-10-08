---
type: Module
title: adapters.receipts
description: Local integrity seal.
resource: repo://src/eija_studio/adapters/receipts.py
tags:
- module
- adapters
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/adapters/receipts.py
  title: adapters/receipts.py
  hash_method: ast-api-v1
  sha256: 9b25d012eeb8af24af6558e47fc78f3c0bd93615ea06cf5db6c1827f4a617d78
notes_baseline: 21efa69e165d8b431353d373d555a482c4c2d3a559cc4d667e25564235a52807
---

# adapters.receipts

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | adapters |
| Code | `repo://src/eija_studio/adapters/receipts.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Local integrity seal. Not third-party attestation; a local administrator can access the key.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`domain/models`](/modules/domain/models.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).

## Referenced by

* [bootstrap](/modules/bootstrap.md) - The only composition root: wires application ports to concrete adapters.
<!-- okf:generated:end links -->
