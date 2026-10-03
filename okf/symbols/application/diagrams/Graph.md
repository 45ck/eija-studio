---
type: Class
title: application.diagrams.Graph
description: A state machine (`kind="state"`) or a flow (`kind="flow"`) of labelled nodes and edges.
resource: repo://src/eija_studio/application/diagrams.py#Graph
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagrams.py#Graph
  title: application/diagrams.py
  hash_method: ast-sig-v1
  sha256: 3b8cc9775671973eb952db308a5a1f9cecaf42097a1de8c579f7dccab4d42e82
notes_baseline: bb5afbb45b25dc3d428ff5f5e76ddf11e3497968e97f10b26e552d7782a5b0d8
---

# application.diagrams.Graph

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/diagrams`](/modules/application/diagrams.md) |
| Signature | `class Graph` |
| Code | `repo://src/eija_studio/application/diagrams.py#Graph` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
A state machine (`kind="state"`) or a flow (`kind="flow"`) of labelled nodes and edges.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['state', 'flow']` |  |
| `title` | `str` |  |
| `nodes` | `tuple[Node, ...]` |  |
| `edges` | `tuple[Edge, ...]` |  |
| `clusters` | `tuple[Cluster, ...]` | `()` |
| `initial` | `str \| None` | `None` |
| `terminals` | `tuple[str, ...]` | `()` |
| `direction` | `Literal['LR', 'TB']` | `'LR'` |
| `legend` | `tuple[tuple[str, str], ...]` | `()` |
| `provenance` | `tuple[str, ...]` | `()` |
| `initial_label` | `str` | `''` |
| `initial_removed` | `str \| None` | `None` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.diagrams.Cluster](/symbols/application/diagrams/Cluster.md) - `class Cluster` in `application/diagrams`.
* [application.diagrams.Edge](/symbols/application/diagrams/Edge.md) - `class Edge` in `application/diagrams`.
* [application.diagrams.Node](/symbols/application/diagrams/Node.md) - `class Node` in `application/diagrams`.

## Referenced by

* [application.diagram_emitters.emit](/symbols/application/diagram_emitters/emit.md) - Serialise a diagram model.
* [application.diagrams.Diagram](/symbols/application/diagrams/Diagram.md) - Type alias `Diagram` in `application/diagrams`.
* [application.diagrams.diff_graph](/symbols/application/diagrams/diff_graph.md) - Baseline vs candidate on one canvas.
* [application.diagrams.impact_graph](/symbols/application/diagrams/impact_graph.md) - The ripple of a change through the modelled dependency chain, taken from `domain.impact.model_impact`: changed rules -> runtime -> state view -> journey -> obl…
* [application.diagrams.journey_graph](/symbols/application/diagrams/journey_graph.md) - One swim-lane per role listing exactly the transitions that role may perform.
* [application.diagrams.mark_blocked](/symbols/application/diagrams/mark_blocked.md) - Make a policy-refused workflow look refused: a red node (graphs) or a note (sequences) naming the codes, plus a provenance line.
* [application.diagrams.state_graph](/symbols/application/diagrams/state_graph.md) - The state machine exactly as the runtime interprets it: states, and one edge per transition.
<!-- okf:generated:end links -->
