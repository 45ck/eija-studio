---
type: Function
title: application.new_system.checked_documents
description: The documents, if the kernel's checks accept them; `PackError` with every problem otherwise.
resource: repo://src/eija_studio/application/new_system.py#checked_documents
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/new_system.py#checked_documents
  title: application/new_system.py
  hash_method: ast-v2
  sha256: cee8a93fdcca72ffa60af865039f91302628caac738559b4d5afcc282e2fff03
notes_baseline: bc9d5d3dc258bc73a74a7a4cd0a38c55264effa97c55cc139e09d84e7fe9d7f8
---

# application.new_system.checked_documents

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/new_system`](/modules/application/new_system.md) |
| Signature | `def checked_documents(documents: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]` |
| Code | `repo://src/eija_studio/application/new_system.py#checked_documents` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The documents, if the kernel's checks accept them; `PackError` with every problem otherwise.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.parse_data](/symbols/domain/data/parse_data.md) - `def parse_data(document: Any, pack_id: str) -> DataModel` in `domain/data`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.pack.PackError](/symbols/domain/pack/PackError.md) - A pack that cannot be used.
* [domain.pack.parse_pack](/symbols/domain/pack/parse_pack.md) - Validate a decoded JSON document as a pack.
* [domain.scenarios.parse_scenarios](/symbols/domain/scenarios/parse_scenarios.md) - `def parse_scenarios(document: Any, pack_id: str) -> Scenarios` in `domain/scenarios`.
* [domain.screens.parse_screens](/symbols/domain/screens/parse_screens.md) - `def parse_screens(document: Any, pack_id: str) -> Screens` in `domain/screens`.

## Referenced by

* [application.describe_system.describe_documents](/symbols/application/describe_system/describe_documents.md) - The documents of a new system described in `text`, checked by the kernel, and what the describer read.
* [application.new_system.sketch_documents](/symbols/application/new_system/sketch_documents.md) - `pack.json` and `data.json` for a system started from a sketch, checked by the kernel's pack check.
* [application.new_system.template_documents](/symbols/application/new_system/template_documents.md) - A copy of a template's documents as a new system: new id and name, the same model, rules, laws, screens and test cases (`scenarios.json`).
<!-- okf:generated:end links -->
