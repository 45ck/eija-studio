---
type: Class
title: application.ports.ReceiptAuthenticator
description: '`class ReceiptAuthenticator(Protocol)` in `application/ports`.'
resource: repo://src/eija_studio/application/ports.py#ReceiptAuthenticator
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/ports.py#ReceiptAuthenticator
  title: application/ports.py
  hash_method: ast-sig-v1
  sha256: ada8930b65b1a0967404c05d3cbc1551b9ef698bfe63ac73e4e1f651e68a4d71
notes_baseline: 4d134a0230d38834dda5c9363e25023e7f92833e84b8dc3a70be6bcbd61cac04
---

# application.ports.ReceiptAuthenticator

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/ports`](/modules/application/ports.md) |
| Signature | `class ReceiptAuthenticator(Protocol)` |
| Code | `repo://src/eija_studio/application/ports.py#ReceiptAuthenticator` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Protocol members

Structural interface implemented by adapters; not a class to instantiate.

* `def seal(self, value: dict[str, Any]) -> dict[str, Any]`
* `def authentic(self, value: dict[str, Any]) -> bool`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio` in `application/service`.
<!-- okf:generated:end links -->
