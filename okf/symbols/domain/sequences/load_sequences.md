---
type: Function
title: domain.sequences.load_sequences
description: The pack's sequences, or None when the pack has no `sequences.json`.
resource: repo://src/eija_studio/domain/sequences.py#load_sequences
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/sequences.py#load_sequences
  title: domain/sequences.py
  hash_method: ast-v2
  sha256: ad0d5fa8b561390e4afa646f8a4bb1eef9e088e1d69a791a96ce44b7de17ce95
notes_baseline: 738cd0c5a80aff40782fb1988a239b6c15e7843815b3d050c7d8a33dd58af29c
---

# domain.sequences.load_sequences

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/sequences`](/modules/domain/sequences.md) |
| Signature | `def load_sequences(pack_directory: str \| Path, pack_id: str) -> Sequences \| None` |
| Code | `repo://src/eija_studio/domain/sequences.py#load_sequences` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The pack's sequences, or None when the pack has no `sequences.json`.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.sequences.SEQUENCES_FILE](/symbols/domain/sequences/SEQUENCES_FILE.md) - Constant `SEQUENCES_FILE` in `domain/sequences`.
* [domain.sequences.Sequences](/symbols/domain/sequences/Sequences.md) - `class Sequences(Contract)` in `domain/sequences`.
* [domain.sequences.parse_sequences](/symbols/domain/sequences/parse_sequences.md) - `def parse_sequences(document: Any, pack_id: str) -> Sequences` in `domain/sequences`.

## Referenced by

* [application.sequences.sequences_for](/symbols/application/sequences/sequences_for.md) - The sequences beside the pack's `pack.json` ("pack"), or scenarios generated from the model in force ("default").
<!-- okf:generated:end links -->
