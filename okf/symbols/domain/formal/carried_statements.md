---
type: Function
title: domain.formal.carried_statements
description: The artifact must carry its own assumptions and limitations (a proof without them is not shown as one).
resource: repo://src/eija_studio/domain/formal.py#carried_statements
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal.py#carried_statements
  title: domain/formal.py
  hash_method: ast-v2
  sha256: 8cce8dfee6b48f3588de28b466ede38725f5e9fa5af8562fec2763bddf123e2d
notes_baseline: 3d39eaef0cca5b81a22952a7de4355ac5c7bb7f0e891e606e19e123ddb94162e
---

# domain.formal.carried_statements

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/formal`](/modules/domain/formal.md) |
| Signature | `def carried_statements(artifact: dict[str, Any]) -> None` |
| Code | `repo://src/eija_studio/domain/formal.py#carried_statements` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The artifact must carry its own assumptions and limitations (a proof without them is not shown as one).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.formal.strings](/symbols/domain/formal/strings.md) - `def strings(container: Any, key: str, where: str, minimum: int=1) -> list[str]` in `domain/formal`.

## Referenced by

* [domain.formal_bend.check](/symbols/domain/formal_bend/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_bend`.
* [domain.formal_bmc.check](/symbols/domain/formal_bmc/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_bmc`.
* [domain.formal_smt.check](/symbols/domain/formal_smt/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_smt`.
<!-- okf:generated:end links -->
