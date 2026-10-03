---
type: Class
title: application.diagrams.Node
description: '`class Node` in `application/diagrams`.'
resource: repo://src/eija_studio/application/diagrams.py#Node
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagrams.py#Node
  title: application/diagrams.py
  hash_method: ast-sig-v1
  sha256: fb00cf2cbfbaf040218be416b9e6354acd65c2b594297d4d5c3dadc9a0010098
notes_baseline: 155cdb75e04d0f42272dce10d3cab2060c6bab1ea9a8d3a5ff198eaff285f68d
---

# application.diagrams.Node

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/diagrams`](/modules/application/diagrams.md) |
| Signature | `class Node` |
| Code | `repo://src/eija_studio/application/diagrams.py#Node` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `id` | `str` |  |
| `label` | `str` |  |
| `status` | `str` | `'same'` |
| `cluster` | `str \| None` | `None` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [application.diagrams.Graph](/symbols/application/diagrams/Graph.md) - A state machine (`kind="state"`) or a flow (`kind="flow"`) of labelled nodes and edges.
* [application.diagrams.diff_graph](/symbols/application/diagrams/diff_graph.md) - Baseline vs candidate on one canvas.
* [application.diagrams.journey_graph](/symbols/application/diagrams/journey_graph.md) - One swim-lane per role listing exactly the transitions that role may perform.
* [application.diagrams.mark_blocked](/symbols/application/diagrams/mark_blocked.md) - Make a policy-refused workflow look refused: a red node (graphs) or a note (sequences) naming the codes, plus a provenance line.
* [application.diagrams.state_graph](/symbols/application/diagrams/state_graph.md) - The state machine exactly as the runtime interprets it: states, and one edge per transition.
<!-- okf:generated:end links -->
