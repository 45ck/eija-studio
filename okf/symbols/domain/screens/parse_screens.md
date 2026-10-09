---
type: Function
title: domain.screens.parse_screens
description: '`def parse_screens(document: Any, pack_id: str) -> Screens` in `domain/screens`.'
resource: repo://src/eija_studio/domain/screens.py#parse_screens
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/screens.py#parse_screens
  title: domain/screens.py
  hash_method: ast-v2
  sha256: 76f0655605aaedab63b2b983b889d49049cb8f1d01c236290a45538baf6ecf82
notes_baseline: 0a50bb2a891b6ca020b71d68a02dbb6cffd002450e2088b2c8296a6e8851770e
---

# domain.screens.parse_screens

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/screens`](/modules/domain/screens.md) |
| Signature | `def parse_screens(document: Any, pack_id: str) -> Screens` |
| Code | `repo://src/eija_studio/domain/screens.py#parse_screens` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.screens.Screens](/symbols/domain/screens/Screens.md) - `class Screens(Contract)` in `domain/screens`.

## Referenced by

* [application.new_system.checked_documents](/symbols/application/new_system/checked_documents.md) - The documents, if the kernel's checks accept them; `PackError` with every problem otherwise.
* [domain.screens.load_screens](/symbols/domain/screens/load_screens.md) - The pack's screens, or None when the pack has no `screens.json`.
<!-- okf:generated:end links -->
