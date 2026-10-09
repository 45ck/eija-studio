---
type: Function
title: application.new_system.sketch_documents
description: '`pack.json` and `data.json` for a system started from a sketch, checked by the kernel''s pack check.'
resource: repo://src/eija_studio/application/new_system.py#sketch_documents
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/new_system.py#sketch_documents
  title: application/new_system.py
  hash_method: ast-v2
  sha256: 8618bfa235c7591df214fc867acf1d02c7d2340655454c732cc989914b95f657
notes_baseline: 7f1ae0b06cfa3303c81604a737ca7d04009e433745da0e065dccd1543bbad69c
---

# application.new_system.sketch_documents

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/new_system`](/modules/application/new_system.md) |
| Signature | `def sketch_documents(name: str, record: str, sketch: str, pack_id: str) -> dict[str, dict[str, Any]]` |
| Code | `repo://src/eija_studio/application/new_system.py#sketch_documents` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
`pack.json` and `data.json` for a system started from a sketch, checked by the kernel's pack check.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.new_system.RECORD](/symbols/application/new_system/RECORD.md) - Constant `RECORD` in `application/new_system`.
* [application.new_system.UNSUPPORTED](/symbols/application/new_system/UNSUPPORTED.md) - Constant `UNSUPPORTED` in `application/new_system`.
* [application.new_system.parse_sketch](/symbols/application/new_system/parse_sketch.md) - The transitions, extra actions and extra roles of a sketch, or `PackError` naming each bad line.
* [domain.models.BASE_GUARDS](/symbols/domain/models/BASE_GUARDS.md) - Constant `BASE_GUARDS` in `domain/models`.
* [domain.pack.PackError](/symbols/domain/pack/PackError.md) - A pack that cannot be used.
<!-- okf:generated:end links -->
