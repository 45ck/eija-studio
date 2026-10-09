---
type: Function
title: application.new_system.template_documents
description: 'A copy of a template''s documents as a new system: new id and name, the same model, rules, laws, screens and test cases (`scenarios.json`).'
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
  sha256: ccd75f898837ad3565fb99a2822b599f72123048f9a9e5d342130ea91383d8aa
notes_baseline: bb1672f9d8629ca55166db787d5459a7d3ed53f4f672fc689602e6ef37047a23
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
A copy of a template's documents as a new system: new id and name, the same model, rules, laws, screens and
test cases (`scenarios.json`).

What belonged only to the template is dropped: its language terms' `repo://` bindings, and any claim of a
hand-written formal model, which was written for the template's id and is not this system's.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.new_system.checked_documents](/symbols/application/new_system/checked_documents.md) - The documents, if the kernel's checks accept them; `PackError` with every problem otherwise.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
