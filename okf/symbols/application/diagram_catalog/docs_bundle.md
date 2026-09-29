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
  sha256: 3c0809017a94ee0d5be4f5d3979ae7bb755cf51817098247b352c60135920052
notes_baseline: 2cc54e06a5828744259c976c368547286541f9eda7a88eaf03b6991f8352cc14
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
