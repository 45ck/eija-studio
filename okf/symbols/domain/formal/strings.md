---
type: Function
title: domain.formal.strings
description: '`def strings(container: Any, key: str, where: str, minimum: int=1) -> list[str]` in `domain/formal`.'
resource: repo://src/eija_studio/domain/formal.py#strings
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal.py#strings
  title: domain/formal.py
  hash_method: ast-v2
  sha256: 5436ca17fba0fc93979adad14e08eacd6a9562b82b37fc4f9a9020bfb1193ae3
notes_baseline: b127f3e889ed1871707ea4d20c5f1fb279469e702550b76eb6397fa283c03018
---

# domain.formal.strings

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/formal`](/modules/domain/formal.md) |
| Signature | `def strings(container: Any, key: str, where: str, minimum: int=1) -> list[str]` |
| Code | `repo://src/eija_studio/domain/formal.py#strings` |
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

## Referenced by

* [domain.formal.carried_statements](/symbols/domain/formal/carried_statements.md) - The artifact must carry its own assumptions and limitations (a proof without them is not shown as one).
<!-- okf:generated:end links -->
