---
type: Class
title: domain.sequences.Message
description: '`class Message(Contract)` in `domain/sequences`.'
resource: repo://src/eija_studio/domain/sequences.py#Message
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/sequences.py#Message
  title: domain/sequences.py
  hash_method: ast-sig-v1
  sha256: fc6ff283566c8b8d679eeb921d0db22c63e0f6c4132dde0931599f415c38524e
notes_baseline: 8bdcb75463aba2a10d718a928f71c01b6fec79e43bcd30862bf7413629cf7be6
---

# domain.sequences.Message

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/sequences`](/modules/domain/sequences.md) |
| Signature | `class Message(Contract)` |
| Code | `repo://src/eija_studio/domain/sequences.py#Message` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `actor` | `str` | `Field(min_length=1, max_length=80)` |
| `action` | `str` | `Field(pattern=ACTION)` |
| `record` | `str` | `Field(default='', max_length=24)` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.sequences.ACTION](/symbols/domain/sequences/ACTION.md) - Constant `ACTION` in `domain/sequences`.

## Referenced by

* [application.sequence_layout.export](/symbols/application/sequence_layout/export.md) - The sequence as Mermaid and PlantUML text, through `diagram_emitters` (Mermaid has no neg: it is written as opt).
* [application.sequence_layout.place](/symbols/application/sequence_layout/place.md) - `def place(pack: Pack, model: Workflow, interaction: Interaction, verdicts: dict[str, dict[str, Any]], cls: st…` in `application/sequence_layout`.
* [application.sequences.default_sequences](/symbols/application/sequences/default_sequences.md) - Scenarios for a pack with no `sequences.json`: one per final state, and one `neg`.
* [domain.sequences.Interaction](/symbols/domain/sequences/Interaction.md) - `class Interaction(Contract)` in `domain/sequences`.
* [domain.sequences.Interaction.record_of](/symbols/domain/sequences/Interaction.record_of.md) - `def record_of(self, message: Message) -> str` in `domain/sequences`.
* [domain.sequences.Operand](/symbols/domain/sequences/Operand.md) - `class Operand(Contract)` in `domain/sequences`.
* [domain.sequences.Step](/symbols/domain/sequences/Step.md) - Type alias `Step` in `domain/sequences`.
* [domain.sequences.messages](/symbols/domain/sequences/messages.md) - Every message, fragments' operands included, in reading order.
<!-- okf:generated:end links -->
