---
type: Type Alias
title: application.ripple.Build
description: Type alias `Build` in `application/ripple`.
resource: repo://src/eija_studio/application/ripple.py#Build
tags:
- symbol
- application
- type-alias
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/ripple.py#Build
  title: application/ripple.py
  hash_method: ast-v2
  sha256: 9d93862e7325dff80154c47ca570fc3c15463f9404556a0e18eeb6a7a9639416
notes_baseline: 6bce21f97d911f66835bbd89e8c540176906b2ed95317a0048d38ae7d43f0233
---

# application.ripple.Build

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | type-alias |
| Module | [`application/ripple`](/modules/application/ripple.md) |
| Signature | `Build = tuple[dict[str, str], int] \| DomainError` |
| Code | `repo://src/eija_studio/application/ripple.py#Build` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.

## Referenced by

* [application.ripple.ripple](/symbols/application/ripple/ripple.md) - Every diagram's effects of going from `base` to `candidate`.
<!-- okf:generated:end links -->
