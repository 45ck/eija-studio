---
type: Function
title: application.new_system.classes
description: A system's record class and each class's attribute names, for naming data-model steps (ADR-0202); None when the system has no class diagram.
resource: repo://src/eija_studio/application/new_system.py#classes
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/new_system.py#classes
  title: application/new_system.py
  hash_method: ast-v2
  sha256: ba9cc64a48d145377e427f54b1871673b9cd6b41e301324c95fd17c9a18a438a
notes_baseline: fd1057bc417fb4fd51cae828195657c4b45c697d1a611a540fa92f6198b45318
---

# application.new_system.classes

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/new_system`](/modules/application/new_system.md) |
| Signature | `def classes(pack: Pack) -> tuple[str, dict[str, list[str]]] \| None` |
| Code | `repo://src/eija_studio/application/new_system.py#classes` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
A system's record class and each class's attribute names, for naming data-model steps (ADR-0202); None when the
system has no class diagram. A draft's held data model counts (`domain.pack.hold`).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.data_for](/symbols/domain/data/data_for.md) - The data model beside this pack's `pack.json`, if it has one: the one a draft holds (ADR-0202), else `data.json`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
