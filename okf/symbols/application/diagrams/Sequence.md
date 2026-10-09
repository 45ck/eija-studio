---
type: Class
title: application.diagrams.Sequence
description: '`class Sequence` in `application/diagrams`.'
resource: repo://src/eija_studio/application/diagrams.py#Sequence
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagrams.py#Sequence
  title: application/diagrams.py
  hash_method: ast-sig-v1
  sha256: c86f703359d802eeca9d7b2e71920b5be84d531466d71a73dd7828160c47ec10
notes_baseline: 3b8bca3b19fd07194fad228df44502278228dd861bc498e9c4dd497241b96eaf
---

# application.diagrams.Sequence

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/diagrams`](/modules/application/diagrams.md) |
| Signature | `class Sequence` |
| Code | `repo://src/eija_studio/application/diagrams.py#Sequence` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `title` | `str` |  |
| `participants` | `tuple[Participant, ...]` |  |
| `steps` | `tuple[Step, ...]` |  |
| `provenance` | `tuple[str, ...]` | `()` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.diagrams.Participant](/symbols/application/diagrams/Participant.md) - `class Participant` in `application/diagrams`.
* [application.diagrams.Step](/symbols/application/diagrams/Step.md) - Type alias `Step` in `application/diagrams`.

## Referenced by

* [application.diagram_emitters.emit](/symbols/application/diagram_emitters/emit.md) - Serialise a diagram model.
* [application.diagrams.Diagram](/symbols/application/diagrams/Diagram.md) - Type alias `Diagram` in `application/diagrams`.
* [application.diagrams.commit_sequence](/symbols/application/diagrams/commit_sequence.md) - The commit protocol of one action, in the order `application.runtime.execute` runs it: authority is checked BEFORE any replay lookup, then replay/operation bin…
* [application.diagrams.mark_blocked](/symbols/application/diagrams/mark_blocked.md) - Make a policy-refused workflow look refused: a red node (graphs) or a note (sequences) naming the codes, plus a provenance line.
* [application.sequence_layout.export](/symbols/application/sequence_layout/export.md) - The sequence as Mermaid and PlantUML text, through `diagram_emitters`, state invariants as notes (Mermaid has no neg: it is written as opt).
<!-- okf:generated:end links -->
