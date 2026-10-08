---
type: Class
title: domain.sequences.Operand
description: '`class Operand(Contract)` in `domain/sequences`.'
resource: repo://src/eija_studio/domain/sequences.py#Operand
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/sequences.py#Operand
  title: domain/sequences.py
  hash_method: ast-sig-v1
  sha256: 67f6317a2417206a924a4f953ed4ba4ead9524ef8b494ebdb413d817179d874b
notes_baseline: f7a2f4c90389957f93eef1ba761a3feb1b9afda731f5ad22a32b449e46efb5ef
---

# domain.sequences.Operand

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/sequences`](/modules/domain/sequences.md) |
| Signature | `class Operand(Contract)` |
| Code | `repo://src/eija_studio/domain/sequences.py#Operand` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `guard` | `str` | `Field(default='', max_length=60)` |
| `steps` | `tuple[Message, ...]` | `Field(min_length=1, max_length=20)` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.sequences.Message](/symbols/domain/sequences/Message.md) - `class Message(Contract)` in `domain/sequences`.

## Referenced by

* [domain.sequences.Fragment](/symbols/domain/sequences/Fragment.md) - `class Fragment(Contract)` in `domain/sequences`.
<!-- okf:generated:end links -->
