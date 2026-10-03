---
type: Constant
title: application.diagram_catalog.VIEW_FORMATS
description: Constant `VIEW_FORMATS` in `application/diagram_catalog`.
resource: repo://src/eija_studio/application/diagram_catalog.py#VIEW_FORMATS
tags:
- symbol
- application
- constant
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagram_catalog.py#VIEW_FORMATS
  title: application/diagram_catalog.py
  hash_method: ast-v2
  sha256: c9ca85cf358d4b2588b23e440b2f4ab581c198d4b9cdd802f80dec20f4e3975c
notes_baseline: 3ae94453020033106d4615fc82957d0b5320d0706391ceec6fcfeafac6515383
---

# application.diagram_catalog.VIEW_FORMATS

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`application/diagram_catalog`](/modules/application/diagram_catalog.md) |
| Signature | `VIEW_FORMATS = dict.fromkeys(('state', 'diff', 'journey', 'impact'), FORMATS) \| {'sequence': ('mermaid', 'plantuml'), 'class': ('mermaid', 'plantuml')}` |
| Code | `repo://src/eija_studio/application/diagram_catalog.py#VIEW_FORMATS` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.diagram_emitters.FORMATS](/symbols/application/diagram_emitters/FORMATS.md) - Constant `FORMATS` in `application/diagram_emitters`.

## Referenced by

* [application.diagram_catalog.case_diagrams](/symbols/application/diagram_catalog/case_diagrams.md) - Every view for one change case as one JSON-friendly payload.
<!-- okf:generated:end links -->
