---
type: Function
title: domain.formal.has_items
description: True if the list at ``key`` is not empty (its items may be of any type).
resource: repo://src/eija_studio/domain/formal.py#has_items
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal.py#has_items
  title: domain/formal.py
  hash_method: ast-v2
  sha256: f4440ab5b07186f8afb7595110780adc43094c4f25b5187bf68c0019e8095005
notes_baseline: 88d331df9f8fb74dc2c6d8c067aa947c6ce23bc58d450f4612d256145f3133d8
---

# domain.formal.has_items

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/formal`](/modules/domain/formal.md) |
| Signature | `def has_items(container: Any, key: str, where: str) -> bool` |
| Code | `repo://src/eija_studio/domain/formal.py#has_items` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
True if the list at ``key`` is not empty (its items may be of any type).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.formal.field](/symbols/domain/formal/field.md) - ``container[key]`` if it is exactly of ``typ`` (``bool`` is not an ``int``); else the artifact is malformed.
<!-- okf:generated:end links -->
