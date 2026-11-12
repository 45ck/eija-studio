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
  sha256: 230a55cade3d687021b3ba424da8f41c1885bda7f5d7878371c268789017f946
notes_baseline: 9fe02ddc558a6b513b203ef3a50f89365145dc51c2d7cf30cc6952a3aa1a8cc4
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

## Referenced by

* [domain.data.check_record](/symbols/domain/data/check_record.md) - Validate a record's values: its attributes with `check_values`, then each reference field, which must hold the id of a stored object of its class (`exists(clas…
<!-- okf:generated:end links -->
