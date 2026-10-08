---
type: Module
title: application.diagram_emitters
description: 'Text emitters for the diagram models in `application.diagrams`: Mermaid, PlantUML and Graphviz DOT.'
resource: repo://src/eija_studio/application/diagram_emitters.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagram_emitters.py
  title: application/diagram_emitters.py
  hash_method: ast-api-v1
  sha256: 83b65ee8299535626fad5640ed2fc605e1ede6a8a4df573b210fc3c2965b549b
notes_baseline: 1ef536f79a65c396c5798595f9e3e48b842b6ad59815ab3db3f3f6e899401929
---

# application.diagram_emitters

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/diagram_emitters.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Text emitters for the diagram models in `application.diagrams`: Mermaid, PlantUML and Graphviz DOT.

Emitters only serialise. They add no information the model does not carry, sort everything they own
(identifier maps, legend rows, class definitions) and end every document with a single newline, so equal
input gives byte-identical output on every platform. Labels are escaped for the target syntax because a
model may come from an untrusted file (`eija render --workflow`).
~~~

## Public symbols

* [`FORMATS`](/symbols/application/diagram_emitters/FORMATS.md) (constant) - no docstring
* [`PALETTE`](/symbols/application/diagram_emitters/PALETTE.md) (constant) - no docstring
* [`emit`](/symbols/application/diagram_emitters/emit.md) (function) - Serialise a diagram model.
* [`safe_ids`](/symbols/application/diagram_emitters/safe_ids.md) (function) - Stable identifier map.

## Internal imports

* [`application/diagrams`](/modules/application/diagrams.md)
* [`domain/models`](/modules/domain/models.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.diagrams](/modules/application/diagrams.md) - Diagram models derived from the executable Workflow (ADR-0019, ADR-0023).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).

## Referenced by

* [application.diagram_catalog](/modules/application/diagram_catalog.md) - Named diagram views over a baseline and an optional candidate Workflow.
* [application.diagram_emitters.FORMATS](/symbols/application/diagram_emitters/FORMATS.md) - Constant `FORMATS` in `application/diagram_emitters`.
* [application.diagram_emitters.PALETTE](/symbols/application/diagram_emitters/PALETTE.md) - Constant `PALETTE` in `application/diagram_emitters`.
* [application.diagram_emitters.emit](/symbols/application/diagram_emitters/emit.md) - Serialise a diagram model.
* [application.diagram_emitters.safe_ids](/symbols/application/diagram_emitters/safe_ids.md) - Stable identifier map.
<!-- okf:generated:end links -->
