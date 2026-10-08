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
  sha256: 41401be6dcedd68dbf7b684add47818fea982c1d94403815e40fbe12601fe3a3
notes_baseline: c8e5dc742aa6186e70b9503d2889e667bc8503b2e815b59bd39ecb597aab559f
---

# application.sequence_layout.export

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/sequence_layout`](/modules/application/sequence_layout.md) |
| Signature | `def export(title: str, placed: dict[str, Any]) -> dict[str, str]` |
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
* [application.diagrams.Message](/symbols/application/diagrams/Message.md) - `class Message` in `application/diagrams`.
* [application.diagrams.Participant](/symbols/application/diagrams/Participant.md) - `class Participant` in `application/diagrams`.
* [application.diagrams.Sequence](/symbols/application/diagrams/Sequence.md) - `class Sequence` in `application/diagrams`.
<!-- okf:generated:end links -->
