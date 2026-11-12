---
type: Function
title: application.scxml.hoisted
description: The transitions each state or composite carries in the chart.
resource: repo://src/eija_studio/application/scxml.py#hoisted
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/scxml.py#hoisted
  title: application/scxml.py
  hash_method: ast-v2
  sha256: 65ee3210008d433bed9a4e1b539ac6e83feb4b2cabe6d3b901a55d0a7d64905f
notes_baseline: d5b384ebfeae27fc5712f403f9f07fc2024eefc042af453f2bb6f31966764e40
---

# application.scxml.hoisted

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/scxml`](/modules/application/scxml.md) |
| Signature | `def hoisted(model: Workflow) -> dict[str, list[Transition]]` |
| Code | `repo://src/eija_studio/application/scxml.py#hoisted` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The transitions each state or composite carries in the chart. Where one action leaves every state inside a
composite (ADR-0232 makes those transitions alike but for their source), the chart carries it once, on the
composite, as UML draws it (ADR-0238). Larger composites are tried first, so the outermost group that fits wins.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [application.scxml.to_scxml](/symbols/application/scxml/to_scxml.md) - The model as an SCXML document.
<!-- okf:generated:end links -->
