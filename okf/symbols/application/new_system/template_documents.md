---
type: Function
title: application.new_system.template_documents
description: 'A copy of a template''s documents as a new system: new id and name, the same model, rules and screens.'
resource: repo://src/eija_studio/application/new_system.py#template_documents
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/new_system.py#template_documents
  title: application/new_system.py
  hash_method: ast-v2
  sha256: 111d3669b222defb052dea22f02b28f4d1c592d6990bd1f5240041802d024f16
notes_baseline: 3411b2bef44e271d53b33aaca1498e07c580436b6db946b15e4ee198e8c6ef6f
---

# application.new_system.template_documents

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/new_system`](/modules/application/new_system.md) |
| Signature | `def template_documents(template: Pack, documents: dict[str, dict[str, Any]], name: str, pack_id: str) -> dict[str, dict[str, Any]]` |
| Code | `repo://src/eija_studio/application/new_system.py#template_documents` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
A copy of a template's documents as a new system: new id and name, the same model, rules and screens.

What belonged only to the template is dropped: its language terms' `repo://` bindings, and any claim of a
hand-written formal model, which was written for the template's id and is not this system's.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
