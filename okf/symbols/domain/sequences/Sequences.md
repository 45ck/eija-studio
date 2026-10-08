---
type: Class
title: domain.sequences.Sequences
description: '`class Sequences(Contract)` in `domain/sequences`.'
resource: repo://src/eija_studio/domain/sequences.py#Sequences
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/sequences.py#Sequences
  title: domain/sequences.py
  hash_method: ast-sig-v1
  sha256: ec0b3589d9e1675567d2d3fbc10e8fec8226d31281b2422eaee271f7f40ca72f
notes_baseline: 41622d14409f7768d2ff3bb0ea289a28e6d0004a48e01b3576ea8420449bc17a
---

# domain.sequences.Sequences

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/sequences`](/modules/domain/sequences.md) |
| Signature | `class Sequences(Contract)` |
| Code | `repo://src/eija_studio/domain/sequences.py#Sequences` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `schema_version` | `Literal['eija.sequences.v1']` | `'eija.sequences.v1'` |
| `id` | `str` | `Field(pattern='^[a-z][a-z0-9-]{0,39}$')` |
| `sequences` | `tuple[Interaction, ...]` | `Field(min_length=1, max_length=30)` |

## Methods

* [`digest`](/symbols/domain/sequences/Sequences.digest.md) - `def digest(self) -> str`
* [`unique`](/symbols/domain/sequences/Sequences.unique.md) - `def unique(self) -> Sequences`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.sequences.Interaction](/symbols/domain/sequences/Interaction.md) - `class Interaction(Contract)` in `domain/sequences`.

## Referenced by

* [application.sequences.check_sequences](/symbols/application/sequences/check_sequences.md) - Every sequence checked by the kernel on `model`; with `base` (the model in force) also on it, for the change.
* [application.sequences.default_sequences](/symbols/application/sequences/default_sequences.md) - Scenarios for a pack with no `sequences.json`: one per final state, and one `neg`.
* [application.sequences.sequences_for](/symbols/application/sequences/sequences_for.md) - The sequences beside the pack's `pack.json` ("pack"), or scenarios generated from the model in force ("default").
* [domain.sequences.Sequences.digest](/symbols/domain/sequences/Sequences.digest.md) - `def digest(self) -> str` in `domain/sequences`.
* [domain.sequences.Sequences.unique](/symbols/domain/sequences/Sequences.unique.md) - `def unique(self) -> Sequences` in `domain/sequences`.
* [domain.sequences.load_sequences](/symbols/domain/sequences/load_sequences.md) - The pack's sequences, or None when the pack has no `sequences.json`.
* [domain.sequences.parse_sequences](/symbols/domain/sequences/parse_sequences.md) - `def parse_sequences(document: Any, pack_id: str) -> Sequences` in `domain/sequences`.
<!-- okf:generated:end links -->
