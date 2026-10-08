---
type: Module
title: application.sequence_layout
description: Where a checked sequence is drawn, and its export (ADR-0185).
resource: repo://src/eija_studio/application/sequence_layout.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/sequence_layout.py
  title: application/sequence_layout.py
  hash_method: ast-api-v1
  sha256: 0898d5f1c284412ffbbb88d57cba29ecf83bfa8ef76984ae1a0e8a8ca650ea06
notes_baseline: efc757ea3d358b2497c698c831df48165cc182e5465d2560081a6252efc27373
---

# application.sequence_layout

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/sequence_layout.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Where a checked sequence is drawn, and its export (ADR-0185).

`place` lays a sequence out deterministically from the kernel's verdicts (`application.sequences`): lifeline columns in
order of first use (actors, then records, then effect channels) and rows top to bottom, so the page only draws boxes
and arrows at the coordinates it is given. A refused message gets a reply; a committed one gets the record's state as a
UML state invariant and its effects as asynchronous messages. `export` writes the same sequence as Mermaid and
PlantUML through the existing `diagram_emitters`.
~~~

## Public symbols

* [`ROW`](/symbols/application/sequence_layout/ROW.md) (constant) - no docstring
* [`export`](/symbols/application/sequence_layout/export.md) (function) - The sequence as Mermaid and PlantUML text, through `diagram_emitters` (Mermaid has no neg: it is written as opt).
* [`place`](/symbols/application/sequence_layout/place.md) (function) - no docstring

## Internal imports

* [`application/diagram_emitters`](/modules/application/diagram_emitters.md)
* [`application/diagrams`](/modules/application/diagrams.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/sequences`](/modules/domain/sequences.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.diagram_emitters](/modules/application/diagram_emitters.md) - Text emitters for the diagram models in `application.diagrams`: Mermaid, PlantUML and Graphviz DOT.
* [application.diagrams](/modules/application/diagrams.md) - Diagram models derived from the executable Workflow (ADR-0019, ADR-0023).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.sequences](/modules/domain/sequences.md) - Sequences: UML interactions between the pack's actors and its records, kept beside the pack (ADR-0185).

## Referenced by

* [application.sequences](/modules/application/sequences.md) - Sequence diagrams the kernel checks (ADR-0185): can this model produce this interaction?
* [application.sequence_layout.ROW](/symbols/application/sequence_layout/ROW.md) - Constant `ROW` in `application/sequence_layout`.
* [application.sequence_layout.export](/symbols/application/sequence_layout/export.md) - The sequence as Mermaid and PlantUML text, through `diagram_emitters` (Mermaid has no neg: it is written as opt).
* [application.sequence_layout.place](/symbols/application/sequence_layout/place.md) - `def place(pack: Pack, model: Workflow, interaction: Interaction, verdicts: dict[str, dict[str, Any]], cls: st…` in `application/sequence_layout`.
<!-- okf:generated:end links -->
