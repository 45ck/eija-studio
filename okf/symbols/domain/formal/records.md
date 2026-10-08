---
type: Function
title: domain.formal.records
description: '`def records(container: Any, key: str, where: str) -> list[dict[str, Any]]` in `domain/formal`.'
resource: repo://src/eija_studio/domain/formal.py#records
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal.py#records
  title: domain/formal.py
  hash_method: ast-v2
  sha256: b124196fc6868d0990e7f3a842977333bbe1577c2d61943cf5c7de75ec6043b8
notes_baseline: f8a664c8bf56de8431d2dd71bff6dc119fa04983251bd0933296cec050ae0250
---

# domain.formal.records

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/formal`](/modules/domain/formal.md) |
| Signature | `def records(container: Any, key: str, where: str) -> list[dict[str, Any]]` |
| Code | `repo://src/eija_studio/domain/formal.py#records` |
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

* [domain.formal.reported_labels](/symbols/domain/formal/reported_labels.md) - The tool's own verdict and check labels may LOWER the status, never raise it.
<!-- okf:generated:end links -->
