---
type: Function
title: application.sequences.record_name
description: 'The record lifeline''s default name and its class: `loan : Loan` when the pack has a data model.'
resource: repo://src/eija_studio/application/sequences.py#record_name
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/sequences.py#record_name
  title: application/sequences.py
  hash_method: ast-v2
  sha256: 145a4767abd970801e594971402c010dbb911fd2907d13c2e67673e7ac096341
notes_baseline: 3b074059129102af9fdb649777b4fa002c74fd5c0170d5b245d4c628527d35c5
---

# application.sequences.record_name

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/sequences`](/modules/application/sequences.md) |
| Signature | `def record_name(pack: Pack) -> tuple[str, str]` |
| Code | `repo://src/eija_studio/application/sequences.py#record_name` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The record lifeline's default name and its class: `loan : Loan` when the pack has a data model.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.data_for](/symbols/domain/data/data_for.md) - The data model beside this pack's `pack.json`, if it has one.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.sequences.check_sequences](/symbols/application/sequences/check_sequences.md) - Every sequence checked by the kernel on `model`; with `base` (the model in force) also on it, for the change.
* [application.sequences.default_sequences](/symbols/application/sequences/default_sequences.md) - Scenarios for a pack with no `sequences.json`: one per final state, and one `neg`.
<!-- okf:generated:end links -->
