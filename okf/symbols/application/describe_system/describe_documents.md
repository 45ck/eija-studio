---
type: Function
title: application.describe_system.describe_documents
description: The documents of a new system described in `text`, checked by the kernel, and what the describer read.
resource: repo://src/eija_studio/application/describe_system.py#describe_documents
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/describe_system.py#describe_documents
  title: application/describe_system.py
  hash_method: ast-v2
  sha256: 01d4dc5b916c79f6d4999ac9770d5b64e8db08ee872a30cfabb83aafe718c1ae
notes_baseline: 8f143f0ad0c516b1cbc79046979941afe9266f71b162203f85b94e8c6821e124
---

# application.describe_system.describe_documents

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/describe_system`](/modules/application/describe_system.md) |
| Signature | `def describe_documents(text: str, name: str, id_for: Callable[[str], str], describer: SystemDescriber) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]` |
| Code | `repo://src/eija_studio/application/describe_system.py#describe_documents` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The documents of a new system described in `text`, checked by the kernel, and what the describer read. The
system is called `name`, or what the describer calls it; `id_for` gives the pack id for a name.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.describe_system.tests_for](/symbols/application/describe_system/tests_for.md) - Test cases for a new system, recorded by the kernel: the way to each end state, and the first step taken by a role that may not take it.
* [application.new_system.checked_documents](/symbols/application/new_system/checked_documents.md) - The documents, if the kernel's checks accept them; `PackError` with every problem otherwise.
* [application.new_system.sketch_documents](/symbols/application/new_system/sketch_documents.md) - `pack.json` and `data.json` for a system started from a sketch, checked by the kernel's pack check.
* [application.ports.SystemDescriber](/symbols/application/ports/SystemDescriber.md) - Turns a description of an app into {name, record, sketch, fields, reading} for "Describe your app" (ADR-0203).
* [domain.pack.parse_pack](/symbols/domain/pack/parse_pack.md) - Validate a decoded JSON document as a pack.
<!-- okf:generated:end links -->
