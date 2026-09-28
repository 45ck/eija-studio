---
type: Method
title: application.service.Studio.layout
description: '`def layout(self, case_id: str, expected: int, change: LayoutChange, principal: Principal) -> dict` in `application/service`.'
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
  sha256: f644a0338feb07659cf1b3b5a2cbc6a475a2afdde96325ee085400fcde48a347
notes_baseline: 180712cfe7c0fa913b712001dd7499ffe5169f882eeb2b683ded621aef5d0880
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
