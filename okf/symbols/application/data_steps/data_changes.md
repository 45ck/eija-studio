---
type: Function
title: application.data_steps.data_changes
description: 'What changed on the class diagram, in words: attributes gained and lost, and required ones made optional or back.'
resource: repo://src/eija_studio/application/data_steps.py#data_changes
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/data_steps.py#data_changes
  title: application/data_steps.py
  hash_method: ast-v2
  sha256: fe8a0ba0d977b0dfb501db2cb4280079a4b16694c2d57d994fe1432c435b7db1
notes_baseline: bd13767b131a5e27ff9251560dda53769189cab95bbdf54f021ef1707f4b3b59
---

# application.data_steps.data_changes

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/data_steps`](/modules/application/data_steps.md) |
| Signature | `def data_changes(before: DataModel \| None, after: DataModel \| None) -> list[str]` |
| Code | `repo://src/eija_studio/application/data_steps.py#data_changes` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
What changed on the class diagram, in words: attributes gained and lost, and required ones made optional or back.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
<!-- okf:generated:end links -->
