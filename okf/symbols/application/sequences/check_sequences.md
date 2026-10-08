---
type: Function
title: application.sequences.check_sequences
description: Every sequence checked by the kernel on `model`; with `base` (the model in force) also on it, for the change.
resource: repo://src/eija_studio/application/sequences.py#check_sequences
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/sequences.py#check_sequences
  title: application/sequences.py
  hash_method: ast-v2
  sha256: a6d0a559cc9a146c7888270d46f516a4f8b3a5fcd42c150d8026769db1e7a3a3
notes_baseline: 014eae4d2ac66f0f61a7dce409ed66689ac09ec52b0c04b3b73a45eb9520a59c
---

# application.sequences.check_sequences

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/sequences`](/modules/application/sequences.md) |
| Signature | `def check_sequences(pack: Pack, model: Workflow, sequences: Sequences, base: Workflow \| None=None) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/sequences.py#check_sequences` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Every sequence checked by the kernel on `model`; with `base` (the model in force) also on it, for the change.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.ghost_diff.ghost_diff](/symbols/application/ghost_diff/ghost_diff.md) - The union of two state machines, each element with its status, and the ordered list of changes.
* [application.sequences.FORMAT](/symbols/application/sequences/FORMAT.md) - Constant `FORMAT` in `application/sequences`.
* [application.sequences.LIMITS](/symbols/application/sequences/LIMITS.md) - Constant `LIMITS` in `application/sequences`.
* [application.sequences.record_name](/symbols/application/sequences/record_name.md) - The record lifeline's default name and its class: `loan : Loan` when the pack has a data model.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.sequences.Sequences](/symbols/domain/sequences/Sequences.md) - `class Sequences(Contract)` in `domain/sequences`.
<!-- okf:generated:end links -->
