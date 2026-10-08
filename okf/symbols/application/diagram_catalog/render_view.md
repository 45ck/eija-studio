---
type: Function
title: application.diagram_catalog.render_view
description: Generated diagram text for one view.
resource: repo://src/eija_studio/application/diagram_catalog.py#render_view
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagram_catalog.py#render_view
  title: application/diagram_catalog.py
  hash_method: ast-v2
  sha256: 35c140626073b5496e1c75a3d3491af3e0230600e4cc1d4647f1b5d8135cdfd9
notes_baseline: 49a84726f5b699fad7cf1efe8b49f468505a4bfde0746946f65958a04ce43e16
---

# application.diagram_catalog.render_view

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/diagram_catalog`](/modules/application/diagram_catalog.md) |
| Signature | `def render_view(view: str, fmt: str, before: Workflow, after: Workflow \| None=None, action: str \| None=None) -> str` |
| Code | `repo://src/eija_studio/application/diagram_catalog.py#render_view` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Generated diagram text for one view. `state`, `journey` and `sequence` describe the candidate when
there is one, else the baseline; `diff` and `impact` require a candidate. A workflow the protected policy
refuses is still drawn, but carries a visible POLICY BLOCKED marker naming the codes (a picture must not
make a change the kernel would refuse look routine).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.diagram_catalog.VIEWS](/symbols/application/diagram_catalog/VIEWS.md) - Constant `VIEWS` in `application/diagram_catalog`.
* [application.diagram_emitters.emit](/symbols/application/diagram_emitters/emit.md) - Serialise a diagram model.
* [application.diagrams.mark_blocked](/symbols/application/diagrams/mark_blocked.md) - Make a policy-refused workflow look refused: a red node (graphs) or a note (sequences) naming the codes, plus a provenance line.
* [application.diagrams.policy_violations](/symbols/application/diagrams/policy_violations.md) - Codes `domain.policy.check_policy` reports for `workflow` (empty: the protected policy accepts it).
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [application.diagram_catalog.case_diagrams](/symbols/application/diagram_catalog/case_diagrams.md) - Every view for one change case as one JSON-friendly payload.
* [application.diagram_catalog.docs_bundle](/symbols/application/diagram_catalog/docs_bundle.md) - Markdown pages for docs/diagrams/, keyed by file name.
* [application.diagram_catalog.html_panels](/symbols/application/diagram_catalog/html_panels.md) - (heading, note, Mermaid text) for `eija render --format html`.
<!-- okf:generated:end links -->
