---
type: Function
title: application.diagram_catalog.docs_bundle
description: Markdown pages for docs/diagrams/, keyed by file name.
resource: repo://src/eija_studio/application/diagram_catalog.py#docs_bundle
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagram_catalog.py#docs_bundle
  title: application/diagram_catalog.py
  hash_method: ast-v2
  sha256: cbe30d29262657a450dab071ae6f9ab7b277f7530e12e0a35d03cc6ea53d0877
notes_baseline: 86694f6bccc348256340b49314e4e8cc882767ec6119ce8dd5942fb4ffd3719c
---

# application.diagram_catalog.docs_bundle

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/diagram_catalog`](/modules/application/diagram_catalog.md) |
| Signature | `def docs_bundle() -> dict[str, str]` |
| Code | `repo://src/eija_studio/application/diagram_catalog.py#docs_bundle` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Markdown pages for docs/diagrams/, keyed by file name. GitHub renders the Mermaid blocks. The drift
check regenerates this and compares bytes with the committed files.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.diagram_catalog.demo_pair](/symbols/application/diagram_catalog/demo_pair.md) - Baseline and the recommend_only candidate the excursion demo produces (rejection source Recommended).
* [application.diagram_catalog.render_view](/symbols/application/diagram_catalog/render_view.md) - Generated diagram text for one view.
<!-- okf:generated:end links -->
