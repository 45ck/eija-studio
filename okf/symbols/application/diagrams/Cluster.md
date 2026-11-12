---
type: Class
title: application.diagrams.Cluster
description: '`class Cluster` in `application/diagrams`.'
resource: repo://src/eija_studio/application/diagrams.py#Cluster
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagrams.py#Cluster
  title: application/diagrams.py
  hash_method: ast-sig-v1
  sha256: 8a362730abe03e3b77df4a89708d8ed601d7a947c5f86ec39b5670b83f811d53
notes_baseline: 22e0b43c012afbd1ba6e1352fd8f99ca8436d3f47256a933a538e5e69832cfcc
---

# application.diagrams.Cluster

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/diagrams`](/modules/application/diagrams.md) |
| Signature | `class Cluster` |
| Code | `repo://src/eija_studio/application/diagrams.py#Cluster` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `id` | `str` |  |
| `label` | `str` |  |
| `parent` | `str \| None` | `None` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [application.diagrams.Graph](/symbols/application/diagrams/Graph.md) - A state machine (`kind="state"`) or a flow (`kind="flow"`) of labelled nodes and edges.
* [application.diagrams.impact_graph](/symbols/application/diagrams/impact_graph.md) - The ripple of a change through the modelled dependency chain, taken from `domain.impact.model_impact`: changed rules -> runtime -> state view -> journey -> obl…
* [application.diagrams.journey_graph](/symbols/application/diagrams/journey_graph.md) - One swim-lane per role listing exactly the transitions that role may perform.
* [application.diagrams.state_graph](/symbols/application/diagrams/state_graph.md) - The state machine exactly as the runtime interprets it: states, and one edge per transition.
<!-- okf:generated:end links -->
