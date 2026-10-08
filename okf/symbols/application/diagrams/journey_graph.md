---
type: Function
title: application.diagrams.journey_graph
description: One swim-lane per role listing exactly the transitions that role may perform.
resource: repo://src/eija_studio/application/diagrams.py#journey_graph
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagrams.py#journey_graph
  title: application/diagrams.py
  hash_method: ast-v2
  sha256: cefa005f036b6531f763e1d02e610527e4b9777d7399d76418d56d83b0bd25d4
notes_baseline: c91636bb0fd3cf4b44f3291a46da8d8916950c195abec22863e3919bed19f0e6
---

# application.diagrams.journey_graph

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/diagrams`](/modules/application/diagrams.md) |
| Signature | `def journey_graph(workflow: Workflow) -> Graph` |
| Code | `repo://src/eija_studio/application/diagrams.py#journey_graph` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
One swim-lane per role listing exactly the transitions that role may perform. Derived from
`Transition.role`, not from prose, so a journey cannot promise an action the runtime would refuse.
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
