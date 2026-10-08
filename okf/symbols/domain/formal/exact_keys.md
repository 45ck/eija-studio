---
type: Function
title: domain.formal.exact_keys
description: '`def exact_keys(artifact: dict[str, Any], keys: frozenset[str]) -> None` in `domain/formal`.'
resource: repo://src/eija_studio/domain/formal.py#exact_keys
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal.py#exact_keys
  title: domain/formal.py
  hash_method: ast-v2
  sha256: daf54d6a93ff69f528b29c8ffe83b6803d01b1d9399e0a79f04b4a92b26bbdd1
notes_baseline: 21dfd258a7c976a43c73a752681d97254b239f59def0720629de9a601e4165a9
---

# domain.formal.exact_keys

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/formal`](/modules/domain/formal.md) |
| Signature | `def exact_keys(artifact: dict[str, Any], keys: frozenset[str]) -> None` |
| Code | `repo://src/eija_studio/domain/formal.py#exact_keys` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.formal.Malformed](/symbols/domain/formal/Malformed.md) - The artifact does not have the declared typed shape (a structural defect, judged FAIL).

## Referenced by

* [domain.formal_bend.check](/symbols/domain/formal_bend/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_bend`.
* [domain.formal_bmc.check](/symbols/domain/formal_bmc/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_bmc`.
* [domain.formal_smt.check](/symbols/domain/formal_smt/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_smt`.
<!-- okf:generated:end links -->
