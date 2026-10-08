---
type: Type Alias
title: application.diagrams.Diagram
description: Type alias `Diagram` in `application/diagrams`.
resource: repo://src/eija_studio/application/diagrams.py#Diagram
tags:
- symbol
- application
- type-alias
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagrams.py#Diagram
  title: application/diagrams.py
  hash_method: ast-v2
  sha256: b2d42e1649d52ac4012f86b3fc020e97ff6b36281ffbad7c54bf491c4bc4c0c4
notes_baseline: 8bcccc87ef8cf9d97ef93f6f6801a35476cfa738e98b78091d1b66f440becbd2
---

# application.diagrams.Diagram

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | type-alias |
| Module | [`application/diagrams`](/modules/application/diagrams.md) |
| Signature | `Diagram = Graph \| Sequence \| ClassModel` |
| Code | `repo://src/eija_studio/application/diagrams.py#Diagram` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.diagrams.ClassModel](/symbols/application/diagrams/ClassModel.md) - `class ClassModel` in `application/diagrams`.
* [application.diagrams.Graph](/symbols/application/diagrams/Graph.md) - A state machine (`kind="state"`) or a flow (`kind="flow"`) of labelled nodes and edges.
* [application.diagrams.Sequence](/symbols/application/diagrams/Sequence.md) - `class Sequence` in `application/diagrams`.

## Referenced by

* [application.diagram_emitters.emit](/symbols/application/diagram_emitters/emit.md) - Serialise a diagram model.
* [application.diagrams.mark_blocked](/symbols/application/diagrams/mark_blocked.md) - Make a policy-refused workflow look refused: a red node (graphs) or a note (sequences) naming the codes, plus a provenance line.
<!-- okf:generated:end links -->
