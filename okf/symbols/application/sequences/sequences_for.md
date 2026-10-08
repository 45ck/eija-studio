---
type: Function
title: application.sequences.sequences_for
description: The sequences beside the pack's `pack.json` ("pack"), or scenarios generated from the model in force ("default").
resource: repo://src/eija_studio/application/sequences.py#sequences_for
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/sequences.py#sequences_for
  title: application/sequences.py
  hash_method: ast-v2
  sha256: dc72f699e187aa88f869f5813f1a49bf322a5eaa4c41c5fe7ba6fa515a10f82a
notes_baseline: 0aefbb8464e6d224ad6bb6ad104839e367ec4271fa0c911165cfcc58bbd6f3b8
---

# application.sequences.sequences_for

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/sequences`](/modules/application/sequences.md) |
| Signature | `def sequences_for(pack: Pack, model: Workflow) -> tuple[Sequences, str]` |
| Code | `repo://src/eija_studio/application/sequences.py#sequences_for` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The sequences beside the pack's `pack.json` ("pack"), or scenarios generated from the model in force ("default").
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.sequences.default_sequences](/symbols/application/sequences/default_sequences.md) - Scenarios for a pack with no `sequences.json`: one per final state, and one `neg`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.pack_directory](/symbols/domain/pack/pack_directory.md) - The directory this exact pack snapshot was read from, or its authored directory, so optional files beside `pack.json` (such as `data.json`) are read from the s…
* [domain.sequences.Sequences](/symbols/domain/sequences/Sequences.md) - `class Sequences(Contract)` in `domain/sequences`.
* [domain.sequences.load_sequences](/symbols/domain/sequences/load_sequences.md) - The pack's sequences, or None when the pack has no `sequences.json`.
<!-- okf:generated:end links -->
