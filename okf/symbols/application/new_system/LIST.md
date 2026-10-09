---
type: Constant
title: application.new_system.LIST
description: Constant `LIST` in `application/new_system`.
resource: repo://src/eija_studio/application/new_system.py#LIST
tags:
- symbol
- application
- constant
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/new_system.py#LIST
  title: application/new_system.py
  hash_method: ast-v2
  sha256: 8199ba2c5e16e597d20079a9e783bc2730bfa37d12bc0e4e3a9af8ca134f0050
notes_baseline: 10e1732d91cda9070f30c72b4279fc98e70cd4f6ba798aee5332eaea46969233
---

# application.new_system.LIST

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`application/new_system`](/modules/application/new_system.md) |
| Signature | `LIST = re.compile('^\\s*(actions\|roles\|people\|agents\|timers\|systems)\\s*:\\s*(.*)$', re.IGNORECASE)` |
| Code | `repo://src/eija_studio/application/new_system.py#LIST` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [application.new_system.parse_sketch](/symbols/application/new_system/parse_sketch.md) - The transitions, extra actions and extra roles of a sketch, or `PackError` naming each bad line.
<!-- okf:generated:end links -->
