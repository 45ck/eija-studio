---
type: Module
title: domain.sequences
description: 'Sequences: UML interactions between the pack''s actors and its records, kept beside the pack (ADR-0185).'
resource: repo://src/eija_studio/domain/sequences.py
tags:
- module
- domain
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/sequences.py
  title: domain/sequences.py
  hash_method: ast-api-v1
  sha256: da3f991e5fd2ebb408c1adc6ee2a72177f656b173b2b3a05942f3cea6c64cef6
notes_baseline: ed6eea18a2458903413c507901892ce00bc50f2fed166db4cb70f8f52cab9a2e
---

# domain.sequences

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | domain |
| Code | `repo://src/eija_studio/domain/sequences.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Sequences: UML interactions between the pack's actors and its records, kept beside the pack (ADR-0185).

A sequence diagram here is a scenario: who sends which action to which record, in order. Lifelines are the pack's
fixture actors (`<actor id> : <role>`) and the records the scenario names; a message is an action. Combined
fragments are the three UML operators a scenario over a state machine needs:

* `opt [guard]`: the operand may or may not happen; what follows must work either way.
* `alt [guard] / [guard]`: one of two to four operands happens; what follows must work after each.
* `neg`: the operand is an invalid trace. The kernel must refuse it, optionally with a named refusal code.

Operands hold messages only; fragments do not nest. This file only describes sequences: whether the model can produce
one is decided by the kernel (`application.sequences`), never here. They live in an optional `sequences.json` beside the
pack's `pack.json`, with their own digest. A pack without one gets scenarios generated from the model in force.
~~~

## Public symbols

* [`ACTION`](/symbols/domain/sequences/ACTION.md) (constant) - no docstring
* [`Fragment`](/symbols/domain/sequences/Fragment.md) (class) - no docstring
* [`Interaction`](/symbols/domain/sequences/Interaction.md) (class) - no docstring
* [`Message`](/symbols/domain/sequences/Message.md) (class) - no docstring
* [`Operand`](/symbols/domain/sequences/Operand.md) (class) - no docstring
* [`RECORD`](/symbols/domain/sequences/RECORD.md) (constant) - no docstring
* [`SEQUENCES_FILE`](/symbols/domain/sequences/SEQUENCES_FILE.md) (constant) - no docstring
* [`Sequences`](/symbols/domain/sequences/Sequences.md) (class) - no docstring
* [`Step`](/symbols/domain/sequences/Step.md) (type-alias) - no docstring
* [`load_sequences`](/symbols/domain/sequences/load_sequences.md) (function) - The pack's sequences, or None when the pack has no `sequences.json`.
* [`messages`](/symbols/domain/sequences/messages.md) (function) - Every message, fragments' operands included, in reading order.
* [`parse_sequences`](/symbols/domain/sequences/parse_sequences.md) (function) - no docstring

## Internal imports

* [`domain/models`](/modules/domain/models.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).

## Referenced by

* [application.sequence_layout](/modules/application/sequence_layout.md) - Where a checked sequence is drawn, and its export (ADR-0185).
* [application.sequences](/modules/application/sequences.md) - Sequence diagrams the kernel checks (ADR-0185): can this model produce this interaction?
* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
* [domain.sequences.ACTION](/symbols/domain/sequences/ACTION.md) - Constant `ACTION` in `domain/sequences`.
* [domain.sequences.Fragment](/symbols/domain/sequences/Fragment.md) - `class Fragment(Contract)` in `domain/sequences`.
* [domain.sequences.Fragment.shape](/symbols/domain/sequences/Fragment.shape.md) - `def shape(self) -> Fragment` in `domain/sequences`.
* [domain.sequences.Interaction.known_records](/symbols/domain/sequences/Interaction.known_records.md) - `def known_records(self) -> Interaction` in `domain/sequences`.
* [domain.sequences.Interaction](/symbols/domain/sequences/Interaction.md) - `class Interaction(Contract)` in `domain/sequences`.
* [domain.sequences.Interaction.record_of](/symbols/domain/sequences/Interaction.record_of.md) - `def record_of(self, message: Message) -> str` in `domain/sequences`.
* [domain.sequences.Message](/symbols/domain/sequences/Message.md) - `class Message(Contract)` in `domain/sequences`.
* [domain.sequences.Operand](/symbols/domain/sequences/Operand.md) - `class Operand(Contract)` in `domain/sequences`.
* [domain.sequences.RECORD](/symbols/domain/sequences/RECORD.md) - Constant `RECORD` in `domain/sequences`.
* [domain.sequences.SEQUENCES_FILE](/symbols/domain/sequences/SEQUENCES_FILE.md) - Constant `SEQUENCES_FILE` in `domain/sequences`.
* [domain.sequences.Sequences.digest](/symbols/domain/sequences/Sequences.digest.md) - `def digest(self) -> str` in `domain/sequences`.
* [domain.sequences.Sequences](/symbols/domain/sequences/Sequences.md) - `class Sequences(Contract)` in `domain/sequences`.
* [domain.sequences.Sequences.unique](/symbols/domain/sequences/Sequences.unique.md) - `def unique(self) -> Sequences` in `domain/sequences`.
* [domain.sequences.Step](/symbols/domain/sequences/Step.md) - Type alias `Step` in `domain/sequences`.
* [domain.sequences.load_sequences](/symbols/domain/sequences/load_sequences.md) - The pack's sequences, or None when the pack has no `sequences.json`.
* [domain.sequences.messages](/symbols/domain/sequences/messages.md) - Every message, fragments' operands included, in reading order.
* [domain.sequences.parse_sequences](/symbols/domain/sequences/parse_sequences.md) - `def parse_sequences(document: Any, pack_id: str) -> Sequences` in `domain/sequences`.
<!-- okf:generated:end links -->
