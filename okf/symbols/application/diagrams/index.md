# Symbols of application.diagrams

# Classes

* [application.diagrams.ClassModel](ClassModel.md) - `class ClassModel` in `application/diagrams`.
* [application.diagrams.ClassNode](ClassNode.md) - `class ClassNode` in `application/diagrams`.
* [application.diagrams.Cluster](Cluster.md) - `class Cluster` in `application/diagrams`.
* [application.diagrams.Edge](Edge.md) - `class Edge` in `application/diagrams`.
* [application.diagrams.Fragment](Fragment.md) - A combined fragment.
* [application.diagrams.Graph](Graph.md) - A state machine (`kind="state"`) or a flow (`kind="flow"`) of labelled nodes and edges.
* [application.diagrams.Member](Member.md) - `class Member` in `application/diagrams`.
* [application.diagrams.Message](Message.md) - `class Message` in `application/diagrams`.
* [application.diagrams.Node](Node.md) - `class Node` in `application/diagrams`.
* [application.diagrams.Note](Note.md) - `class Note` in `application/diagrams`.
* [application.diagrams.Participant](Participant.md) - `class Participant` in `application/diagrams`.
* [application.diagrams.Relation](Relation.md) - `class Relation` in `application/diagrams`.
* [application.diagrams.Sequence](Sequence.md) - `class Sequence` in `application/diagrams`.

# Constants

* [application.diagrams.BLOCKED_ID](BLOCKED_ID.md) - Constant `BLOCKED_ID` in `application/diagrams`.
* [application.diagrams.CONTRACTS](CONTRACTS.md) - Constant `CONTRACTS` in `application/diagrams`.
* [application.diagrams.DDD_ROLE](DDD_ROLE.md) - Constant `DDD_ROLE` in `application/diagrams`.
* [application.diagrams.GUARD_FAILURES](GUARD_FAILURES.md) - Constant `GUARD_FAILURES` in `application/diagrams`.
* [application.diagrams.IMPACT_LEGEND](IMPACT_LEGEND.md) - Constant `IMPACT_LEGEND` in `application/diagrams`.
* [application.diagrams.LEGEND_TEXT](LEGEND_TEXT.md) - Constant `LEGEND_TEXT` in `application/diagrams`.
* [application.diagrams.NODE_KIND](NODE_KIND.md) - Constant `NODE_KIND` in `application/diagrams`.
* [application.diagrams.SHARED_NODE](SHARED_NODE.md) - Constant `SHARED_NODE` in `application/diagrams`.
* [application.diagrams.STATUS_ORDER](STATUS_ORDER.md) - Constant `STATUS_ORDER` in `application/diagrams`.

# Functions

* [application.diagrams.class_model](class_model.md) - Domain contracts introspected from the Pydantic models.
* [application.diagrams.commit_sequence](commit_sequence.md) - The commit protocol of one action, in the order `application.runtime.execute` runs it: authority is checked BEFORE any replay lookup, then replay/operation binding, CAS on the instance version, state guard, state write,…
* [application.diagrams.diff_graph](diff_graph.md) - Baseline vs candidate on one canvas.
* [application.diagrams.diff_summary](diff_summary.md) - Structured diff of two workflows: states, and transitions by action with each changed field's before and after.
* [application.diagrams.impact_graph](impact_graph.md) - The ripple of a change through the modelled dependency chain, taken from `domain.impact.model_impact`: changed rules -> runtime -> state view -> journey -> obligation -> receipt -> review packet -> decision.
* [application.diagrams.journey_graph](journey_graph.md) - One swim-lane per role listing exactly the transitions that role may perform.
* [application.diagrams.mark_blocked](mark_blocked.md) - Make a policy-refused workflow look refused: a red node (graphs) or a note (sequences) naming the codes, plus a provenance line.
* [application.diagrams.policy_violations](policy_violations.md) - Codes `domain.policy.check_policy` reports for `workflow` (empty: the protected policy accepts it).
* [application.diagrams.state_graph](state_graph.md) - The state machine exactly as the runtime interprets it: states, and one edge per transition.

# Type Aliases

* [application.diagrams.Diagram](Diagram.md) - Type alias `Diagram` in `application/diagrams`.
* [application.diagrams.Status](Status.md) - Type alias `Status` in `application/diagrams`.
* [application.diagrams.Step](Step.md) - Type alias `Step` in `application/diagrams`.
