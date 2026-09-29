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
  sha256: 2ead4cbf6d7bcc6eba8de48d6470abc47ae4e9cde0d3ccb2bc7812438f035b6e
notes_baseline: 4fa8cbc0d41346748fada1673e1e593682b34c5289b17f0290031d1f2bc396cd
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
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [application.diagrams.Graph](/symbols/application/diagrams/Graph.md) - A state machine (`kind="state"`) or a flow (`kind="flow"`) of labelled nodes and edges.
* [application.diagrams.impact_graph](/symbols/application/diagrams/impact_graph.md) - The ripple of a change through the modelled dependency chain, taken from `domain.impact.model_impact`: changed rules -> runtime -> state view -> journey -> obl…
* [application.diagrams.journey_graph](/symbols/application/diagrams/journey_graph.md) - One swim-lane per role listing exactly the transitions that role may perform.
<!-- okf:generated:end links -->
