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
  sha256: 897e4c12c4b6a6ff68431b554fee43ba44ae211133f8f267f05e3eec26853fe3
notes_baseline: d992a19d40a7ae9579bedf142e555d39e4ee729e876b03f394cdbbf83f416854
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
