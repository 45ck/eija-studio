---
type: Method
title: application.service.Studio.layout
description: '`def layout(self, case_id: str, expected: int, change: LayoutChange, principal: Principal) -> dict[str, Any]` in `application/service`.'
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
  hash_method: ast-v2
  sha256: 1449920c1a78b234202f86ecacb3fcc7444a4b1ad8749293895fba0c8915ede1
notes_baseline: bd8087595ab8ebc1ec8c2d2a392474ea55b1ae5100e050e39fc0fdd7c224bd36
---

# application.service.Studio.layout

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def layout(self, case_id: str, expected: int, change: LayoutChange, principal: Principal) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service.py#Studio.layout` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.LayoutChange](/symbols/domain/models/LayoutChange.md) - `class LayoutChange(Contract)` in `domain/models`.
* [domain.models.Principal](/symbols/domain/models/Principal.md) - `class Principal(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
