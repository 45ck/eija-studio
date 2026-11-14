---
type: Function
title: application.diagrams.impact_graph
description: 'The ripple of a change through the modelled dependency chain, taken from `domain.impact.model_impact`: changed rules -> runtime -> state view -> journey -> obligation -> receipt -> review packet -> decision.'
resource: repo://src/eija_studio/application/diagrams.py#impact_graph
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagrams.py#impact_graph
  title: application/diagrams.py
  hash_method: ast-v2
  sha256: f6712d5b9348b77449f424ced4cd58abca5401b1f09908dcc62a2d1266c4459d
notes_baseline: 5ce3b487c6251a9fbbbee3fbb4b1fd8e62eeefa096d52acbe61f218568fd9349
---

# application.diagrams.impact_graph

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/diagrams`](/modules/application/diagrams.md) |
| Signature | `def impact_graph(before: Workflow, after: Workflow, impact: dict[str, Any] \| None=None) -> Graph` |
| Code | `repo://src/eija_studio/application/diagrams.py#impact_graph` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The ripple of a change through the modelled dependency chain, taken from `domain.impact.model_impact`:
changed rules -> runtime -> state view -> journey -> obligation -> receipt -> review packet -> decision.
The mapping is the model's own; consequences outside it are not drawn (see the `envelope` note).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.diagrams.Cluster](/symbols/application/diagrams/Cluster.md) - `class Cluster` in `application/diagrams`.
* [application.diagrams.Graph](/symbols/application/diagrams/Graph.md) - A state machine (`kind="state"`) or a flow (`kind="flow"`) of labelled nodes and edges.
* [domain.impact.model_impact](/symbols/domain/impact/model_impact.md) - The ripple of a change.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
