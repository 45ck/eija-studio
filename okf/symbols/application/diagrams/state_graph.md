---
type: Function
title: application.diagrams.state_graph
description: 'The state machine exactly as the runtime interprets it: states, and one edge per transition.'
resource: repo://src/eija_studio/application/diagrams.py#state_graph
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagrams.py#state_graph
  title: application/diagrams.py
  hash_method: ast-v2
  sha256: d3d63f9fa2a9e239d89c0424781566cca7758d0f990af71724b2f6c9e9fb19a5
notes_baseline: f0d9f99ca663c1b82adc4d3968c2c5c428f2c5095014346f44cde795c0cf299b
---

# application.diagrams.state_graph

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/diagrams`](/modules/application/diagrams.md) |
| Signature | `def state_graph(workflow: Workflow, *, role: str='workflow') -> Graph` |
| Code | `repo://src/eija_studio/application/diagrams.py#state_graph` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The state machine exactly as the runtime interprets it: states, and one edge per transition.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.diagrams.Edge](/symbols/application/diagrams/Edge.md) - `class Edge` in `application/diagrams`.
* [application.diagrams.Graph](/symbols/application/diagrams/Graph.md) - A state machine (`kind="state"`) or a flow (`kind="flow"`) of labelled nodes and edges.
* [application.diagrams.Node](/symbols/application/diagrams/Node.md) - `class Node` in `application/diagrams`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
