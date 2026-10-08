---
type: Function
title: application.sequences.default_sequences
description: 'Scenarios for a pack with no `sequences.json`: one per final state, and one `neg`.'
resource: repo://src/eija_studio/application/sequences.py#default_sequences
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/sequences.py#default_sequences
  title: application/sequences.py
  hash_method: ast-v2
  sha256: 8a9a9433bed817cf1b99a4f3600e168e0edc465d2e5c93d82e31700df1d211e0
notes_baseline: 54e342ae90100332bb3a3f92a9bd78f68653ceeb47014ec7b7ac1e867a73bf8a
---

# application.sequences.default_sequences

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/sequences`](/modules/application/sequences.md) |
| Signature | `def default_sequences(pack: Pack, model: Workflow) -> Sequences` |
| Code | `repo://src/eija_studio/application/sequences.py#default_sequences` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Scenarios for a pack with no `sequences.json`: one per final state, and one `neg`. Generated from `model`, the
model in force, so a change is checked against the scenarios it had.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.sequences.MAX_DEFAULTS](/symbols/application/sequences/MAX_DEFAULTS.md) - Constant `MAX_DEFAULTS` in `application/sequences`.
* [application.sequences.record_name](/symbols/application/sequences/record_name.md) - The record lifeline's default name and its class: `loan : Loan` when the pack has a data model.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.sequences.Interaction](/symbols/domain/sequences/Interaction.md) - `class Interaction(Contract)` in `domain/sequences`.
* [domain.sequences.Message](/symbols/domain/sequences/Message.md) - `class Message(Contract)` in `domain/sequences`.
* [domain.sequences.Sequences](/symbols/domain/sequences/Sequences.md) - `class Sequences(Contract)` in `domain/sequences`.

## Referenced by

* [application.sequences.sequences_for](/symbols/application/sequences/sequences_for.md) - The sequences beside the pack's `pack.json` ("pack"), or scenarios generated from the model in force ("default").
<!-- okf:generated:end links -->
