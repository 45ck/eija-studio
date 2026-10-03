---
type: Function
title: application.diagram_catalog.html_panels
description: (heading, note, Mermaid text) for `eija render --format html`.
resource: repo://src/eija_studio/application/diagram_catalog.py#html_panels
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagram_catalog.py#html_panels
  title: application/diagram_catalog.py
  hash_method: ast-v2
  sha256: a4721e6ce509bcf2a91ab9450418b8ea83f6407d752abdec6ae68b24d69ce7be
notes_baseline: 5dc1809ba49c4beb5a81d3ca0669029b097f5256380e948696d889a1c43ba0c7
---

# application.diagram_catalog.html_panels

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/diagram_catalog`](/modules/application/diagram_catalog.md) |
| Signature | `def html_panels(view: str, before: Workflow, after: Workflow \| None, action: str \| None=None) -> list[tuple[str, str, str]]` |
| Code | `repo://src/eija_studio/application/diagram_catalog.py#html_panels` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
(heading, note, Mermaid text) for `eija render --format html`. `view="all"` is every view that applies:
one commit-protocol panel per action, and no diff or ripple when there is no candidate.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.diagram_catalog.VIEWS](/symbols/application/diagram_catalog/VIEWS.md) - Constant `VIEWS` in `application/diagram_catalog`.
* [application.diagram_catalog.render_view](/symbols/application/diagram_catalog/render_view.md) - Generated diagram text for one view.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
