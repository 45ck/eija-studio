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
  sha256: e30a544c6e5bacc9f91b7edaff62db11398bc90b2aac96dd5a6b95aee62c3abe
notes_baseline: 5c2ededfcbca3bed685e3a5ceb2ae7cbc819214b99086749d5b482a5e2f4e5fb
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
composite, as UML draws it (ADR-0240). Larger composites are tried first, so the outermost group that fits wins.
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
