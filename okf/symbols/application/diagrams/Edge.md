---
type: Class
title: application.diagrams.Edge
description: '`class Edge` in `application/diagrams`.'
resource: repo://src/eija_studio/application/diagrams.py#Edge
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagrams.py#Edge
  title: application/diagrams.py
  hash_method: ast-sig-v1
  sha256: 29933811247a8bdc1871cb3553eee73392b158901dabb93b126a45ecc6e4f405
notes_baseline: 10e7914d38941edfae30aba61a7341433023b469d3f8300e1bf89bb3b8d2ad3f
---

# application.diagrams.Edge

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/diagrams`](/modules/application/diagrams.md) |
| Signature | `class Edge` |
| Code | `repo://src/eija_studio/application/diagrams.py#Edge` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `source` | `str` |  |
| `target` | `str` |  |
| `label` | `str` | `''` |
| `status` | `str` | `'same'` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [application.diagrams.Graph](/symbols/application/diagrams/Graph.md) - A state machine (`kind="state"`) or a flow (`kind="flow"`) of labelled nodes and edges.
* [application.diagrams.journey_graph](/symbols/application/diagrams/journey_graph.md) - One swim-lane per role listing exactly the transitions that role may perform.
* [application.diagrams.state_graph](/symbols/application/diagrams/state_graph.md) - The state machine exactly as the runtime interprets it: states, and one edge per transition.
<!-- okf:generated:end links -->
