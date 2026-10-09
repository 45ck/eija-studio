---
type: Function
title: application.sequence_layout.export
description: 'The sequence as Mermaid and PlantUML text, through `diagram_emitters`, state invariants as notes (Mermaid has no neg: it is written as opt).'
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
  sha256: 018a0196c97bcb95bbc3009b0417b45d63e981290390e2b5a03e52ef407d66c9
notes_baseline: 13b82bfc325dcb714695780dc9435b1c7ce77927e31333d5edea4562f3253b74
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
The sequence as Mermaid and PlantUML text, through `diagram_emitters`, state invariants as notes (Mermaid has no
neg: it is written as opt).
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
<!-- okf:generated:end links -->
