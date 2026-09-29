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
  sha256: b6c7e952be151d6df7ff4a8ab92bd7cc5c2dd73126c57d2b841ebe6e776e391e
notes_baseline: 83dd880e0072b6a7af2c8e226aaeffa21d33b8ae3917d90779c8a02d54fcace9
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

* [application.diagram_catalog.demo_pair](/symbols/application/diagram_catalog/demo_pair.md) - Baseline and the demo candidate: the default pack's baseline with its first supported meaning applied.
* [application.diagram_catalog.render_view](/symbols/application/diagram_catalog/render_view.md) - Generated diagram text for one view.
<!-- okf:generated:end links -->
