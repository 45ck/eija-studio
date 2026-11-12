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
  sha256: f06cf2f5e200f71af74c234630975fb12b9a990c6917aa5ea69cd7057e1c4515
notes_baseline: 53b9f3392ca37150b9e7f5e36234a8c8a4d2736e9b0be9f5cebf851f98445df3
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
