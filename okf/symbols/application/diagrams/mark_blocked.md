---
type: Function
title: application.diagrams.mark_blocked
description: 'Make a policy-refused workflow look refused: a red node (graphs) or a note (sequences) naming the codes, plus a provenance line.'
resource: repo://src/eija_studio/application/diagrams.py#mark_blocked
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagrams.py#mark_blocked
  title: application/diagrams.py
  hash_method: ast-v2
  sha256: 38534786831751b1f71db545a9b3ad441edc41b4567054ee229f81def6e8b80d
notes_baseline: aaf1cf86127d0e269620b8b078f9961600c025f86f6bcc2844df19335ecb1ccc
---

# application.diagrams.mark_blocked

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/diagrams`](/modules/application/diagrams.md) |
| Signature | `def mark_blocked(diagram: Diagram, violations: tuple[str, ...]) -> Diagram` |
| Code | `repo://src/eija_studio/application/diagrams.py#mark_blocked` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Make a policy-refused workflow look refused: a red node (graphs) or a note (sequences) naming the
codes, plus a provenance line. Without it a protected-authority change would draw like any other edit.
The class diagram describes the fixed contracts, not a workflow, so it is returned unchanged.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.diagrams.BLOCKED_ID](/symbols/application/diagrams/BLOCKED_ID.md) - Constant `BLOCKED_ID` in `application/diagrams`.
* [application.diagrams.Diagram](/symbols/application/diagrams/Diagram.md) - Type alias `Diagram` in `application/diagrams`.
* [application.diagrams.Graph](/symbols/application/diagrams/Graph.md) - A state machine (`kind="state"`) or a flow (`kind="flow"`) of labelled nodes and edges.
* [application.diagrams.Node](/symbols/application/diagrams/Node.md) - `class Node` in `application/diagrams`.
* [application.diagrams.Note](/symbols/application/diagrams/Note.md) - `class Note` in `application/diagrams`.
* [application.diagrams.Sequence](/symbols/application/diagrams/Sequence.md) - `class Sequence` in `application/diagrams`.

## Referenced by

* [application.diagram_catalog.render_view](/symbols/application/diagram_catalog/render_view.md) - Generated diagram text for one view.
<!-- okf:generated:end links -->
