---
type: Function
title: application.scxml.event_data
description: 'What the sender of an event attaches: the actor as the directory knows it (None if unknown) and the version.'
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
  sha256: ec19315236c9f1483e287b2c32c679b08089629a0a360ec8abed7ce947b0c76e
notes_baseline: e2b36715aaf23958a4d7906ef177625d456f319a24eb1ea33ae058dff6668a7c
---

# application.scxml.event_data

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/scxml`](/modules/application/scxml.md) |
| Signature | `def event_data(actor: dict[str, Any] \| None, expected_version: int) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/scxml.py#event_data` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
What the sender of an event attaches: the actor as the directory knows it (None if unknown) and the version.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
