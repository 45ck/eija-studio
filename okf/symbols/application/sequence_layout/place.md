---
type: Function
title: application.sequence_layout.place
description: '`def place(pack: Pack, model: Workflow, interaction: Interaction, verdicts: dict[str, dict[str, Any]], cls: st…` in `application/sequence_layout`.'
resource: repo://src/eija_studio/application/sequence_layout.py#place
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/sequence_layout.py#place
  title: application/sequence_layout.py
  hash_method: ast-v2
  sha256: 39e3f50a8f019b555a5525b93e0b7f6c4b2dbc97f0ace99ad4df749e41ffe6c7
notes_baseline: 400663d92de3e2fe782664f6b3e06466fc2b2dee3a904d7d1ca91990f8b56469
---

# application.sequence_layout.place

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/sequence_layout`](/modules/application/sequence_layout.md) |
| Signature | `def place(pack: Pack, model: Workflow, interaction: Interaction, verdicts: dict[str, dict[str, Any]], cls: str) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/sequence_layout.py#place` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.sequence_layout.ROW](/symbols/application/sequence_layout/ROW.md) - Constant `ROW` in `application/sequence_layout`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.sequences.Interaction](/symbols/domain/sequences/Interaction.md) - `class Interaction(Contract)` in `domain/sequences`.
* [domain.sequences.Message](/symbols/domain/sequences/Message.md) - `class Message(Contract)` in `domain/sequences`.
<!-- okf:generated:end links -->
