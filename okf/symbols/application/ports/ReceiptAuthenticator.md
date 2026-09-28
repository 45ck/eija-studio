---
type: Class
title: application.ports.ReceiptAuthenticator
description: '`class ReceiptAuthenticator(Protocol)` in `application/ports` (the source has no docstring).'
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
  sha256: ff87a21da10fb101588a00821cd4ce7daef816437f2ae6d21a6f216e717d94f4
---

# application.ports.ReceiptAuthenticator

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/ports`](/modules/application/ports.md) |
| Signature | `class ReceiptAuthenticator(Protocol)` |
| Code | `repo://src/eija_studio/application/ports.py#ReceiptAuthenticator` |
| Hash | `ast-sig-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._

## Protocol members

Structural interface implemented by adapters; not a class to instantiate.

* `def seal(self, value: dict) -> dict`
* `def authentic(self, value: dict) -> bool`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio` in `application/service` (the source has no docstring).
<!-- okf:generated:end links -->
