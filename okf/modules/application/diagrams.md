---
type: Module
title: application.diagrams
description: Diagram models derived from the executable Workflow (ADR-0019, ADR-0023).
resource: repo://src/eija_studio/application/diagrams.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagrams.py
  title: application/diagrams.py
  hash_method: ast-api-v1
  sha256: 49a01fb0303b64974b85b503a45ba22a373ec668aca86fa148307db16cdab64e
notes_baseline: dea0b4093fe67149ebf7ce46c0b10cac31c15a758278c084253f656bdfd5cbab
---

# application.diagrams

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/diagrams.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Diagram models derived from the executable Workflow (ADR-0019, ADR-0023).

Every builder here is a pure function of domain values: a `Workflow`, a `model_impact` report or the
Pydantic contracts themselves. There is no second source of truth and no hand-drawn element. Builders
produce a small format-neutral intermediate model; `diagram_emitters` turns it into Mermaid, PlantUML
or Graphviz DOT text.

What this establishes: a diagram is a deterministic projection, so reordering the definition of the
same workflow cannot change the output and the text can be regenerated and compared byte-for-byte.
What it does NOT establish: that the model is correct, that a projection is complete beyond the
mapping in `domain.impact`, or that a reader understood it. Parts of a picture are modelled rather
than derived: the commit-protocol order (checked against the real runtime by a spy test, not read
from it) and the DDD stereotypes (a curated vocabulary). A picture is a review aid, not evidence.
~~~

## Public symbols

* [`BLOCKED_ID`](/symbols/application/diagrams/BLOCKED_ID.md) (constant) - no docstring
* [`CONTRACTS`](/symbols/application/diagrams/CONTRACTS.md) (constant) - no docstring
* [`ClassModel`](/symbols/application/diagrams/ClassModel.md) (class) - no docstring
* [`ClassNode`](/symbols/application/diagrams/ClassNode.md) (class) - no docstring
* [`Cluster`](/symbols/application/diagrams/Cluster.md) (class) - no docstring
* [`DDD_ROLE`](/symbols/application/diagrams/DDD_ROLE.md) (constant) - no docstring
* [`Diagram`](/symbols/application/diagrams/Diagram.md) (type-alias) - no docstring
* [`Edge`](/symbols/application/diagrams/Edge.md) (class) - no docstring
* [`Fragment`](/symbols/application/diagrams/Fragment.md) (class) - A conditional block (`opt`): the steps happen only when `label` holds.
* [`GUARD_FAILURES`](/symbols/application/diagrams/GUARD_FAILURES.md) (constant) - no docstring
* [`Graph`](/symbols/application/diagrams/Graph.md) (class) - A state machine (`kind="state"`) or a flow (`kind="flow"`) of labelled nodes and edges.
* [`IMPACT_LEGEND`](/symbols/application/diagrams/IMPACT_LEGEND.md) (constant) - no docstring
* [`LEGEND_TEXT`](/symbols/application/diagrams/LEGEND_TEXT.md) (constant) - no docstring
* [`Member`](/symbols/application/diagrams/Member.md) (class) - no docstring
* [`Message`](/symbols/application/diagrams/Message.md) (class) - no docstring
* [`NODE_KIND`](/symbols/application/diagrams/NODE_KIND.md) (constant) - no docstring
* [`Node`](/symbols/application/diagrams/Node.md) (class) - no docstring
* [`Note`](/symbols/application/diagrams/Note.md) (class) - no docstring
* [`Participant`](/symbols/application/diagrams/Participant.md) (class) - no docstring
* [`Relation`](/symbols/application/diagrams/Relation.md) (class) - no docstring
* [`SHARED_NODE`](/symbols/application/diagrams/SHARED_NODE.md) (constant) - no docstring
* [`STATUS_ORDER`](/symbols/application/diagrams/STATUS_ORDER.md) (constant) - no docstring
* [`Sequence`](/symbols/application/diagrams/Sequence.md) (class) - no docstring
* [`Status`](/symbols/application/diagrams/Status.md) (type-alias) - no docstring
* [`Step`](/symbols/application/diagrams/Step.md) (type-alias) - no docstring
* [`class_model`](/symbols/application/diagrams/class_model.md) (function) - Domain contracts introspected from the Pydantic models.
* [`commit_sequence`](/symbols/application/diagrams/commit_sequence.md) (function) - The commit protocol of one action, in the order `application.runtime.execute` runs it: authority is checked BEFORE any…
* [`diff_graph`](/symbols/application/diagrams/diff_graph.md) (function) - Baseline vs candidate on one canvas.
* [`diff_summary`](/symbols/application/diagrams/diff_summary.md) (function) - Structured diff of two workflows: states, and transitions by action with each changed field's before and after.
* [`impact_graph`](/symbols/application/diagrams/impact_graph.md) (function) - The ripple of a change through the modelled dependency chain, taken from `domain.impact.model_impact`: changed rules ->…
* [`journey_graph`](/symbols/application/diagrams/journey_graph.md) (function) - One swim-lane per role listing exactly the transitions that role may perform.
* [`mark_blocked`](/symbols/application/diagrams/mark_blocked.md) (function) - Make a policy-refused workflow look refused: a red node (graphs) or a note (sequences) naming the codes, plus a provena…
* [`policy_violations`](/symbols/application/diagrams/policy_violations.md) (function) - Codes `domain.policy.check_policy` reports for `workflow` (empty: the protected policy accepts it).
* [`state_graph`](/symbols/application/diagrams/state_graph.md) (function) - The state machine exactly as the runtime interprets it: states, and one edge per transition.

## Internal imports

* [`domain/change_case`](/modules/domain/change_case.md)
* [`domain/impact`](/modules/domain/impact.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/policy`](/modules/domain/policy.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.change_case](/modules/domain/change_case.md) - Module `domain/change_case` (no module docstring).
* [domain.impact](/modules/domain/impact.md) - Module `domain/impact` (no module docstring).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.policy](/modules/domain/policy.md) - Generic policy: coherence with a domain pack's declared action catalog, the pack's laws, and declared effects.

## Referenced by

* [application.diagram_catalog](/modules/application/diagram_catalog.md) - Named diagram views over a baseline and an optional candidate Workflow.
* [application.diagram_emitters](/modules/application/diagram_emitters.md) - Text emitters for the diagram models in `application.diagrams`: Mermaid, PlantUML and Graphviz DOT.
* [application.plan](/modules/application/plan.md) - Plan mode for the PlayIDE chat (ADR-0156): an AI proposes a change as numbered typed steps; the person accepts or rejects each one and sees what the accepted o…
* [application.review](/modules/application/review.md) - Review a model change in PlayIDE instead of a pull request (ADR-0158).
* [application.diagrams.BLOCKED_ID](/symbols/application/diagrams/BLOCKED_ID.md) - Constant `BLOCKED_ID` in `application/diagrams`.
* [application.diagrams.CONTRACTS](/symbols/application/diagrams/CONTRACTS.md) - Constant `CONTRACTS` in `application/diagrams`.
* [application.diagrams.ClassModel](/symbols/application/diagrams/ClassModel.md) - `class ClassModel` in `application/diagrams`.
* [application.diagrams.ClassNode](/symbols/application/diagrams/ClassNode.md) - `class ClassNode` in `application/diagrams`.
* [application.diagrams.Cluster](/symbols/application/diagrams/Cluster.md) - `class Cluster` in `application/diagrams`.
* [application.diagrams.DDD_ROLE](/symbols/application/diagrams/DDD_ROLE.md) - Constant `DDD_ROLE` in `application/diagrams`.
* [application.diagrams.Diagram](/symbols/application/diagrams/Diagram.md) - Type alias `Diagram` in `application/diagrams`.
* [application.diagrams.Edge](/symbols/application/diagrams/Edge.md) - `class Edge` in `application/diagrams`.
* [application.diagrams.Fragment](/symbols/application/diagrams/Fragment.md) - A conditional block (`opt`): the steps happen only when `label` holds.
* [application.diagrams.GUARD_FAILURES](/symbols/application/diagrams/GUARD_FAILURES.md) - Constant `GUARD_FAILURES` in `application/diagrams`.
* [application.diagrams.Graph](/symbols/application/diagrams/Graph.md) - A state machine (`kind="state"`) or a flow (`kind="flow"`) of labelled nodes and edges.
* [application.diagrams.IMPACT_LEGEND](/symbols/application/diagrams/IMPACT_LEGEND.md) - Constant `IMPACT_LEGEND` in `application/diagrams`.
* [application.diagrams.LEGEND_TEXT](/symbols/application/diagrams/LEGEND_TEXT.md) - Constant `LEGEND_TEXT` in `application/diagrams`.
* [application.diagrams.Member](/symbols/application/diagrams/Member.md) - `class Member` in `application/diagrams`.
* [application.diagrams.Message](/symbols/application/diagrams/Message.md) - `class Message` in `application/diagrams`.
* [application.diagrams.NODE_KIND](/symbols/application/diagrams/NODE_KIND.md) - Constant `NODE_KIND` in `application/diagrams`.
* [application.diagrams.Node](/symbols/application/diagrams/Node.md) - `class Node` in `application/diagrams`.
* [application.diagrams.Note](/symbols/application/diagrams/Note.md) - `class Note` in `application/diagrams`.
* [application.diagrams.Participant](/symbols/application/diagrams/Participant.md) - `class Participant` in `application/diagrams`.
* [application.diagrams.Relation](/symbols/application/diagrams/Relation.md) - `class Relation` in `application/diagrams`.
* [application.diagrams.SHARED_NODE](/symbols/application/diagrams/SHARED_NODE.md) - Constant `SHARED_NODE` in `application/diagrams`.
* [application.diagrams.STATUS_ORDER](/symbols/application/diagrams/STATUS_ORDER.md) - Constant `STATUS_ORDER` in `application/diagrams`.
* [application.diagrams.Sequence](/symbols/application/diagrams/Sequence.md) - `class Sequence` in `application/diagrams`.
* [application.diagrams.Status](/symbols/application/diagrams/Status.md) - Type alias `Status` in `application/diagrams`.
* [application.diagrams.Step](/symbols/application/diagrams/Step.md) - Type alias `Step` in `application/diagrams`.
* [application.diagrams.class_model](/symbols/application/diagrams/class_model.md) - Domain contracts introspected from the Pydantic models.
* [application.diagrams.commit_sequence](/symbols/application/diagrams/commit_sequence.md) - The commit protocol of one action, in the order `application.runtime.execute` runs it: authority is checked BEFORE any replay lookup, then replay/operation bin…
* [application.diagrams.diff_graph](/symbols/application/diagrams/diff_graph.md) - Baseline vs candidate on one canvas.
* [application.diagrams.diff_summary](/symbols/application/diagrams/diff_summary.md) - Structured diff of two workflows: states, and transitions by action with each changed field's before and after.
* [application.diagrams.impact_graph](/symbols/application/diagrams/impact_graph.md) - The ripple of a change through the modelled dependency chain, taken from `domain.impact.model_impact`: changed rules -> runtime -> state view -> journey -> obl…
* [application.diagrams.journey_graph](/symbols/application/diagrams/journey_graph.md) - One swim-lane per role listing exactly the transitions that role may perform.
* [application.diagrams.mark_blocked](/symbols/application/diagrams/mark_blocked.md) - Make a policy-refused workflow look refused: a red node (graphs) or a note (sequences) naming the codes, plus a provenance line.
* [application.diagrams.policy_violations](/symbols/application/diagrams/policy_violations.md) - Codes `domain.policy.check_policy` reports for `workflow` (empty: the protected policy accepts it).
* [application.diagrams.state_graph](/symbols/application/diagrams/state_graph.md) - The state machine exactly as the runtime interprets it: states, and one edge per transition.
<!-- okf:generated:end links -->
