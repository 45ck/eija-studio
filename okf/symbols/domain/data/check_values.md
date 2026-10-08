---
type: Function
title: domain.data.check_values
description: Validate a record's values against its entity.
resource: repo://src/eija_studio/domain/data.py#check_values
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/data.py#check_values
  title: domain/data.py
  hash_method: ast-v2
  sha256: 1d4e03a363f5be62822ae07680920b0d00ad97149e2fb3a6488e2712226fd4b7
notes_baseline: d471c7c96d07a8ad4db41b950a21711d441933cf5e298b49a7c2667ddef64d6b
---

# domain.data.check_values

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/data`](/modules/domain/data.md) |
| Signature | `def check_values(entity: Entity, values: dict[str, Any]) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/domain/data.py#check_values` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Validate a record's values against its entity. Empty text and None count as missing. Returns the clean values.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.Entity](/symbols/domain/data/Entity.md) - `class Entity(Contract)` in `domain/data`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
<!-- okf:generated:end links -->
