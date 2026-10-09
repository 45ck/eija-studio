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
  sha256: 296d214c7c4a5dd0e4810d31f3fc02a8737cd7f4562093d9a2d274d52184e532
notes_baseline: 43a4834816db3798efa4e8c4b260249b6e6645c719e21fef920ede69830cd6e0
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

* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
