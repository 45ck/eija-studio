---
type: Function
title: application.diagrams.diff_graph
description: Baseline vs candidate on one canvas.
resource: repo://src/eija_studio/application/diagrams.py#diff_graph
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagrams.py#diff_graph
  title: application/diagrams.py
  hash_method: ast-v2
  sha256: f578b8dfb3386a27f756c3cb5c1ec782261c1159652d8e29f3ea7103c3d67d8b
notes_baseline: a0d296c637241bcffb3e72f9887262f3fc18d67d0f4f4324d6cfb3e1517ab828
---

# application.diagrams.diff_graph

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/diagrams`](/modules/application/diagrams.md) |
| Signature | `def diff_graph(before: Workflow, after: Workflow) -> Graph` |
| Code | `repo://src/eija_studio/application/diagrams.py#diff_graph` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Baseline vs candidate on one canvas. Edge status: an edge only in `after` is added, only in `before`
removed, same endpoints with any changed field (`domain.impact.changed_fields`) changed, and a `~` label
names the fields. A state is added or removed by membership and `changed` when its incident edges differ or
it is (or was) the initial state of a workflow whose initial state moved, which makes the ripple around an
edit visible.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.diagrams.Graph](/symbols/application/diagrams/Graph.md) - A state machine (`kind="state"`) or a flow (`kind="flow"`) of labelled nodes and edges.
* [application.diagrams.Node](/symbols/application/diagrams/Node.md) - `class Node` in `application/diagrams`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
