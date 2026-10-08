---
type: Function
title: application.new_system.system_id
description: A pack id for a new system called `name`, unlike every id in `taken`.
resource: repo://src/eija_studio/application/new_system.py#system_id
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/new_system.py#system_id
  title: application/new_system.py
  hash_method: ast-v2
  sha256: 28140247570ff73ebe5901c7ff194733932aff2795bd4052a7c6ebe4e0dc6d63
notes_baseline: cee4cdc16cc0d97972c28ff9877395e7609c1d8c459123fe7ca223d46fada68e
---

# application.new_system.system_id

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/new_system`](/modules/application/new_system.md) |
| Signature | `def system_id(name: str, taken: set[str]) -> str` |
| Code | `repo://src/eija_studio/application/new_system.py#system_id` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
A pack id for a new system called `name`, unlike every id in `taken`.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
