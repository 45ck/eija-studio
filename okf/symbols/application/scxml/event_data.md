---
type: Function
title: application.scxml.event_data
description: 'What the sender of an event attaches: the actor as the directory knows it (None if unknown), the version, the record''s value of each guarded attribute in `attributes`, for a `timed` model how long it has been in its sta…'
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
  sha256: ad4cb74d788621b942fc7c1420fa1a07b0596b3cb26d4d25999ad8fdfe31f777
notes_baseline: 6380c2572b5c904c50e3c5b4b4019cbd68abef2bb0acd3fa24f221aaed58cbd4
---

# application.scxml.event_data

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/scxml`](/modules/application/scxml.md) |
| Signature | `def event_data(actor: dict[str, Any] \| None, expected_version: int, values: dict[str, Any] \| None=None, attributes: tuple[str, ...]=(), elapsed: float \| None=None, timed: bool=False, objects: dict[str, str \| None] \| None=None) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/scxml.py#event_data` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
What the sender of an event attaches: the actor as the directory knows it (None if unknown), the version, the
record's value of each guarded attribute in `attributes`, for a `timed` model how long it has been in its state
(`elapsed`, None when unknown), and for a model with linked objects the state of each (`objects`, by link).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
