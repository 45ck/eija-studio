---
type: Function
title: domain.formal.digest
description: '`def digest(container: Any, key: str, where: str) -> str` in `domain/formal`.'
resource: repo://src/eija_studio/domain/formal.py#digest
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal.py#digest
  title: domain/formal.py
  hash_method: ast-v2
  sha256: fba6d5b1b4db00636ed92bfd29a0468168ec7fc23240b55b963e3701deefb39f
notes_baseline: a1cc64fb2e7f38ecb92a11e5cba393796e97b333c11a057b23ad5db789a5f3da
---

# domain.formal.digest

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/formal`](/modules/domain/formal.md) |
| Signature | `def digest(container: Any, key: str, where: str) -> str` |
| Code | `repo://src/eija_studio/domain/formal.py#digest` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.formal.Malformed](/symbols/domain/formal/Malformed.md) - The artifact does not have the declared typed shape (a structural defect, judged FAIL).
* [domain.formal.field](/symbols/domain/formal/field.md) - ``container[key]`` if it is exactly of ``typ`` (``bool`` is not an ``int``); else the artifact is malformed.
<!-- okf:generated:end links -->
