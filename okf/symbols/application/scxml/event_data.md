---
type: Function
title: application.scxml.event_data
description: 'What the sender of an event attaches: the actor as the directory knows it (None if unknown), the version, and the record''s value of each guarded attribute in `attributes`.'
resource: repo://src/eija_studio/application/scxml.py#event_data
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/scxml.py#event_data
  title: application/scxml.py
  hash_method: ast-v2
  sha256: 66990a53a5fc7641b839267f0805950f975a68753bcdb616d7c4d270fae6c25c
notes_baseline: edeb84c28564d655fa2f6b4fa943c5e7c920a7f804d513d23d729e411f59ffa3
---

# application.scxml.event_data

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/scxml`](/modules/application/scxml.md) |
| Signature | `def event_data(actor: dict[str, Any] \| None, expected_version: int, values: dict[str, Any] \| None=None, attributes: tuple[str, ...]=()) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/scxml.py#event_data` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
What the sender of an event attaches: the actor as the directory knows it (None if unknown), the version, and
the record's value of each guarded attribute in `attributes`.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
