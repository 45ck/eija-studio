---
type: Function
title: application.new_system.parse_sketch
description: The transitions, extra actions and extra roles of a sketch, or `PackError` naming each bad line.
resource: repo://src/eija_studio/application/new_system.py#parse_sketch
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/new_system.py#parse_sketch
  title: application/new_system.py
  hash_method: ast-v2
  sha256: 548cac8261ff5107f8c4159a414c9d16561b62fb6a081b317063379576197678
notes_baseline: fae8d2cc2298bb1e4559bfef4861435a458db7dd5907558d1b3b401467f2e15c
---

# application.new_system.parse_sketch

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/new_system`](/modules/application/new_system.md) |
| Signature | `def parse_sketch(text: str) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/new_system.py#parse_sketch` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The transitions, extra actions and extra roles of a sketch, or `PackError` naming each bad line.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.new_system.LIST](/symbols/application/new_system/LIST.md) - Constant `LIST` in `application/new_system`.
* [application.new_system.MAX_LINES](/symbols/application/new_system/MAX_LINES.md) - Constant `MAX_LINES` in `application/new_system`.
* [application.new_system.SKETCH_HELP](/symbols/application/new_system/SKETCH_HELP.md) - Constant `SKETCH_HELP` in `application/new_system`.
* [domain.pack.PackError](/symbols/domain/pack/PackError.md) - A pack that cannot be used.

## Referenced by

* [application.new_system.sketch_documents](/symbols/application/new_system/sketch_documents.md) - `pack.json` and `data.json` for a system started from a sketch, checked by the kernel's pack check.
<!-- okf:generated:end links -->
