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
  sha256: 38edc9efc817653844ba7caee40ae4f5cdca8cf775504e34f4ed8b70caa885e9
notes_baseline: 1bbae6552221905da1d68c5321683b16273f1ad31be6bf8d8fbc071a76fbdac6
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
The state machine exactly as the runtime interprets it: states, and one edge per transition. Composite states
(ADR-0237) are drawn as boxes around the states they hold.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.diagrams.Cluster](/symbols/application/diagrams/Cluster.md) - `class Cluster` in `application/diagrams`.
* [application.diagrams.Edge](/symbols/application/diagrams/Edge.md) - `class Edge` in `application/diagrams`.
* [application.diagrams.Graph](/symbols/application/diagrams/Graph.md) - A state machine (`kind="state"`) or a flow (`kind="flow"`) of labelled nodes and edges.
* [application.diagrams.Node](/symbols/application/diagrams/Node.md) - `class Node` in `application/diagrams`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
