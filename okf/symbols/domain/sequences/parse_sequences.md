---
type: Function
title: domain.sequences.parse_sequences
description: '`def parse_sequences(document: Any, pack_id: str) -> Sequences` in `domain/sequences`.'
resource: repo://src/eija_studio/domain/sequences.py#parse_sequences
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/sequences.py#parse_sequences
  title: domain/sequences.py
  hash_method: ast-v2
  sha256: a533da0f9470c1a921f25e0f2931018a9f0621a9b83d67b945de033a9cabac55
notes_baseline: 31c5fa3fd319ea8a64218ffe4bf0161b1a1ced82fc9a08f59eab603c686f35d7
---

# domain.sequences.parse_sequences

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/sequences`](/modules/domain/sequences.md) |
| Signature | `def parse_sequences(document: Any, pack_id: str) -> Sequences` |
| Code | `repo://src/eija_studio/domain/sequences.py#parse_sequences` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.sequences.Sequences](/symbols/domain/sequences/Sequences.md) - `class Sequences(Contract)` in `domain/sequences`.

## Referenced by

* [domain.sequences.load_sequences](/symbols/domain/sequences/load_sequences.md) - The pack's sequences, or None when the pack has no `sequences.json`.
<!-- okf:generated:end links -->
