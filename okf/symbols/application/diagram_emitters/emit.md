---
type: Function
title: application.diagram_emitters.emit
description: Serialise a diagram model.
resource: repo://src/eija_studio/application/diagram_emitters.py#emit
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagram_emitters.py#emit
  title: application/diagram_emitters.py
  hash_method: ast-v2
  sha256: d089fb1d005369cd8bdf367d04e8e876f76527aa8dfc1338da538d674b6ffdba
notes_baseline: b84c221b32fa762c032643141b824c1ea27052ded4fa6a796a8eaa51cdf79a20
---

# application.diagram_emitters.emit

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/diagram_emitters`](/modules/application/diagram_emitters.md) |
| Signature | `def emit(diagram: Diagram, fmt: str) -> str` |
| Code | `repo://src/eija_studio/application/diagram_emitters.py#emit` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Serialise a diagram model. Raises DomainError FORMAT_UNSUPPORTED for a kind/format with no emitter.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.diagram_emitters.FORMATS](/symbols/application/diagram_emitters/FORMATS.md) - Constant `FORMATS` in `application/diagram_emitters`.
* [application.diagrams.ClassModel](/symbols/application/diagrams/ClassModel.md) - `class ClassModel` in `application/diagrams`.
* [application.diagrams.Diagram](/symbols/application/diagrams/Diagram.md) - Type alias `Diagram` in `application/diagrams`.
* [application.diagrams.Graph](/symbols/application/diagrams/Graph.md) - A state machine (`kind="state"`) or a flow (`kind="flow"`) of labelled nodes and edges.
* [application.diagrams.Sequence](/symbols/application/diagrams/Sequence.md) - `class Sequence` in `application/diagrams`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.

## Referenced by

* [application.diagram_catalog.render_view](/symbols/application/diagram_catalog/render_view.md) - Generated diagram text for one view.
* [application.sequence_layout.export](/symbols/application/sequence_layout/export.md) - The sequence as Mermaid and PlantUML text, through `diagram_emitters` (Mermaid has no neg: it is written as opt).
<!-- okf:generated:end links -->
