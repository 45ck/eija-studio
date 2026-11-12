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
  sha256: 3becc3221dd65e9a2daa0e6bb3f5b0c62eff8ca91255f5040d690b64fd5a4467
notes_baseline: 3d3aaa3a23311cb124f9536c3f4ebf889cd21e1b0b582fec6f7f4b16118a877f
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
