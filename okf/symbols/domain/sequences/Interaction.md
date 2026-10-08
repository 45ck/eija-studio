---
type: Class
title: domain.sequences.Interaction
description: '`class Interaction(Contract)` in `domain/sequences`.'
resource: repo://src/eija_studio/domain/sequences.py#Interaction
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/sequences.py#Interaction
  title: domain/sequences.py
  hash_method: ast-sig-v1
  sha256: e390b85b516f52b004e8dd64220e2f2f69c89ff1aff5a685b745a9de22ca4805
notes_baseline: bf977c3875b4997e90989bbc575e3072be1519f48d552e44e37c2ff3a479058a
---

# domain.sequences.Interaction

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/sequences`](/modules/domain/sequences.md) |
| Signature | `class Interaction(Contract)` |
| Code | `repo://src/eija_studio/domain/sequences.py#Interaction` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `id` | `str` | `Field(pattern='^[a-z][a-z0-9-]{0,39}$')` |
| `title` | `str` | `Field(min_length=1, max_length=80)` |
| `records` | `tuple[str, ...]` | `Field(default=('record',), min_length=1, max_length=3)` |
| `steps` | `tuple[Step, ...]` | `Field(min_length=1, max_length=40)` |

## Methods

* [`known_records`](/symbols/domain/sequences/Interaction.known_records.md) - `def known_records(self) -> Interaction`
* [`record_of`](/symbols/domain/sequences/Interaction.record_of.md) - `def record_of(self, message: Message) -> str`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.sequences.Message](/symbols/domain/sequences/Message.md) - `class Message(Contract)` in `domain/sequences`.
* [domain.sequences.Step](/symbols/domain/sequences/Step.md) - Type alias `Step` in `domain/sequences`.

## Referenced by

* [application.sequence_layout.export](/symbols/application/sequence_layout/export.md) - The sequence as Mermaid and PlantUML text, through `diagram_emitters` (Mermaid has no neg: it is written as opt).
* [application.sequence_layout.place](/symbols/application/sequence_layout/place.md) - `def place(pack: Pack, model: Workflow, interaction: Interaction, verdicts: dict[str, dict[str, Any]], cls: st…` in `application/sequence_layout`.
* [application.sequences.default_sequences](/symbols/application/sequences/default_sequences.md) - Scenarios for a pack with no `sequences.json`: one per final state, and one `neg`.
* [domain.sequences.Interaction.known_records](/symbols/domain/sequences/Interaction.known_records.md) - `def known_records(self) -> Interaction` in `domain/sequences`.
* [domain.sequences.Interaction.record_of](/symbols/domain/sequences/Interaction.record_of.md) - `def record_of(self, message: Message) -> str` in `domain/sequences`.
* [domain.sequences.Sequences](/symbols/domain/sequences/Sequences.md) - `class Sequences(Contract)` in `domain/sequences`.
<!-- okf:generated:end links -->
