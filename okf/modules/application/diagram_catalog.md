---
type: Module
title: application.diagram_catalog
description: Named diagram views over a baseline and an optional candidate Workflow.
resource: repo://src/eija_studio/application/diagram_catalog.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagram_catalog.py
  title: application/diagram_catalog.py
  hash_method: ast-api-v1
  sha256: 54ecee0a717158be6c5659abe1e89363ca991edbcaf4d267d13ad4e8ff42c1ee
notes_baseline: 544fc8f1b471b4e41cc09fdcad5407dfc2860580c40db37be709380e9814142e
---

# application.diagram_catalog

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/diagram_catalog.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Named diagram views over a baseline and an optional candidate Workflow.

This is the single entry used by the CLI (`eija render`), the HTTP endpoint and the committed docs, so
all three show the same generated text for the same model (ADR-0019, ADR-0023).
~~~

## Public symbols

* [`VIEWS`](/symbols/application/diagram_catalog/VIEWS.md) (constant) - no docstring
* [`VIEW_FORMATS`](/symbols/application/diagram_catalog/VIEW_FORMATS.md) (constant) - no docstring
* [`case_diagrams`](/symbols/application/diagram_catalog/case_diagrams.md) (function) - Every view for one change case as one JSON-friendly payload.
* [`demo_pair`](/symbols/application/diagram_catalog/demo_pair.md) (function) - Baseline and the recommend_only candidate the excursion demo produces (rejection source Recommended).
* [`docs_bundle`](/symbols/application/diagram_catalog/docs_bundle.md) (function) - Markdown pages for docs/diagrams/, keyed by file name.
* [`html_panels`](/symbols/application/diagram_catalog/html_panels.md) (function) - (heading, note, Mermaid text) for `eija render --format html`.
* [`render_view`](/symbols/application/diagram_catalog/render_view.md) (function) - Generated diagram text for one view.

## Internal imports

* [`application/diagram_emitters`](/modules/application/diagram_emitters.md)
* [`application/diagrams`](/modules/application/diagrams.md)
* [`domain/impact`](/modules/domain/impact.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/policy`](/modules/domain/policy.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.diagram_emitters](/modules/application/diagram_emitters.md) - Text emitters for the diagram models in `application.diagrams`: Mermaid, PlantUML and Graphviz DOT.
* [application.diagrams](/modules/application/diagrams.md) - Diagram models derived from the executable Workflow (ADR-0019, ADR-0023).
* [domain.impact](/modules/domain/impact.md) - Module `domain/impact` (no module docstring).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.policy](/modules/domain/policy.md) - Generic policy: coherence with a domain pack's declared action catalog, the pack's laws, and declared effects.

## Referenced by

* [interfaces.cli](/modules/interfaces/cli.md) - Module `interfaces/cli` (no module docstring).
* [interfaces.http](/modules/interfaces/http.md) - Loopback-only local adapter.
* [application.diagram_catalog.VIEWS](/symbols/application/diagram_catalog/VIEWS.md) - Constant `VIEWS` in `application/diagram_catalog`.
* [application.diagram_catalog.VIEW_FORMATS](/symbols/application/diagram_catalog/VIEW_FORMATS.md) - Constant `VIEW_FORMATS` in `application/diagram_catalog`.
* [application.diagram_catalog.case_diagrams](/symbols/application/diagram_catalog/case_diagrams.md) - Every view for one change case as one JSON-friendly payload.
* [application.diagram_catalog.demo_pair](/symbols/application/diagram_catalog/demo_pair.md) - Baseline and the recommend_only candidate the excursion demo produces (rejection source Recommended).
* [application.diagram_catalog.docs_bundle](/symbols/application/diagram_catalog/docs_bundle.md) - Markdown pages for docs/diagrams/, keyed by file name.
* [application.diagram_catalog.html_panels](/symbols/application/diagram_catalog/html_panels.md) - (heading, note, Mermaid text) for `eija render --format html`.
* [application.diagram_catalog.render_view](/symbols/application/diagram_catalog/render_view.md) - Generated diagram text for one view.
<!-- okf:generated:end links -->
