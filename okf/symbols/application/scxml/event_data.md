---
type: Function
title: application.scxml.event_data
description: 'What the sender of an event attaches: the actor as the directory knows it (None if unknown), the version, the record''s value of each guarded attribute in `attributes`, and, for a `timed` model, how long it has been in i…'
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
  sha256: 62eba84febf252a31beeafc3fbcb4dbd5393299e81545221ad55d942da68987c
notes_baseline: e5552f89d285b6d82ea0a762600047d2afd9f8c3ddb3dacdd9e727f447b7edc1
---

# application.scxml.event_data

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/scxml`](/modules/application/scxml.md) |
| Signature | `def event_data(actor: dict[str, Any] \| None, expected_version: int, values: dict[str, Any] \| None=None, attributes: tuple[str, ...]=(), elapsed: float \| None=None, timed: bool=False) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/scxml.py#event_data` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
What the sender of an event attaches: the actor as the directory knows it (None if unknown), the version, the
record's value of each guarded attribute in `attributes`, and, for a `timed` model, how long it has been in its state
(`elapsed`, None when unknown).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
