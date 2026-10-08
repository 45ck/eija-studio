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
  sha256: 13f82bfcd4c3f39fd4252076c3597ff379b49c70909ed9fcfa423af258356139
notes_baseline: 37c7be597f77d55bfe30a4bcc0526b31ef8172d075cf68e271bf2ef0c337d39e
---

# application.new_system.LIST

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`application/new_system`](/modules/application/new_system.md) |
| Signature | `LIST = re.compile('^\\s*(actions\|roles)\\s*:\\s*(.*)$', re.IGNORECASE)` |
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
