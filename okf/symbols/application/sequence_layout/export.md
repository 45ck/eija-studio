---
type: Function
title: application.sequence_layout.export
description: 'The sequence as Mermaid and PlantUML text, through `diagram_emitters` (Mermaid has no neg: it is written as opt).'
resource: repo://src/eija_studio/application/sequence_layout.py#export
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/sequence_layout.py#export
  title: application/sequence_layout.py
  hash_method: ast-v2
  sha256: 0eb98776cba69d4e87e17cfee41ab312ea20b5ef181deb157bc6904fd255e513
notes_baseline: 3ae84eb836c9ce96b958e65be1888f1878b06e121a9d8c1bda5ff5755ccf9fe2
---

# application.sequence_layout.export

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/sequence_layout`](/modules/application/sequence_layout.md) |
| Signature | `def export(interaction: Interaction, placed: dict[str, Any]) -> dict[str, str]` |
| Code | `repo://src/eija_studio/application/sequence_layout.py#export` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The sequence as Mermaid and PlantUML text, through `diagram_emitters` (Mermaid has no neg: it is written as opt).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.diagram_emitters.emit](/symbols/application/diagram_emitters/emit.md) - Serialise a diagram model.
* [application.diagrams.Fragment](/symbols/application/diagrams/Fragment.md) - A combined fragment.
* [application.diagrams.Participant](/symbols/application/diagrams/Participant.md) - `class Participant` in `application/diagrams`.
* [application.diagrams.Sequence](/symbols/application/diagrams/Sequence.md) - `class Sequence` in `application/diagrams`.
* [domain.sequences.Interaction](/symbols/domain/sequences/Interaction.md) - `class Interaction(Contract)` in `domain/sequences`.
* [domain.sequences.Message](/symbols/domain/sequences/Message.md) - `class Message(Contract)` in `domain/sequences`.
<!-- okf:generated:end links -->
