---
type: Method
title: application.service.Studio.layout
description: '`def layout(self, case_id: str, expected: int, change: LayoutChange, principal: Principal) -> dict` in `application/service` (the source has no docstring).'
resource: repo://src/eija_studio/application/service.py#Studio.layout
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.layout
  title: application/service.py
  hash_method: ast-v1
  sha256: 639c570225012d6e4163f75046eaa4375d126518f9241c05556821937a1dc4ab
---

# application.service.Studio.layout

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def layout(self, case_id: str, expected: int, change: LayoutChange, principal: Principal) -> dict` |
| Code | `repo://src/eija_studio/application/service.py#Studio.layout` |
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.LayoutChange](/symbols/domain/models/LayoutChange.md) - `class LayoutChange(Contract)` in `domain/models` (the source has no docstring).
* [domain.models.Principal](/symbols/domain/models/Principal.md) - `class Principal(Contract)` in `domain/models` (the source has no docstring).
<!-- okf:generated:end links -->
