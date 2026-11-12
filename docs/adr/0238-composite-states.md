# ADR-0238: Composite states

* Status: accepted
* Date: 2026-11-12
* Lane: kernel / executable UML

## Context and problem statement

Issue #93, item 3. A state machine with a dozen states reads better when related states sit in a box: "deciding" holds awaiting approval and escalated, "paying out" holds approved and payout failed. UML calls these composite states, and SCXML has them natively. Until now a workflow was a flat list of states, so the grouping lived only in people's heads.

## Decision drivers

* The kernel decides, and it stays one interpreter. A record is in one plain state, as it always has been, and every checker keeps working on that.
* A composite must mean the same thing everywhere it appears: the model, the diagrams, PlayIDE's canvas and the SCXML chart.
* An independent engine should confirm that the hierarchy changes nothing about what the machine does.
* Every existing model, digest, hash, oracle and recording keeps its exact bytes.

## Considered options

* Composites as a tree over the plain states, with transitions still between plain states. The kernel runs the flat machine, and an action that leaves every state of a composite is drawn and exported once, on the composite (chosen).
* Transitions whose source or target names a composite, expanded by the kernel at run time: closer to UML's notation, but every reader of `from_state` and `to_state` (policy, laws, oracle, diff, importers, PlayIDE) would need the expansion, so a missed one would disagree with the kernel. ADR-0232 already lets one action leave several states, which is what a transition from a composite means once it is flattened.
* Orthogonal regions, where a record is in several states at once: a different record shape (a set of states, not one), so every checker changes. Revisit when a pack needs it.

## Decision outcome

**The model.** A workflow may carry `composites`, up to 16 of `{name, states, initial}`. `states` are its children, which are plain states or other composites, and `initial` is the child a transition into it enters first. They must form a tree: names are unique and differ from every state, each child is known and has one parent, each composite's initial is one of its children, and no composite holds itself. When there are none, the field is left out of every dump, so flat models keep their bytes and semantic hash. The semantic hash sorts composites and their children, because they are sets.

`Workflow.parent`, `ancestors`, `leaves` and `entry` answer the questions a view needs: which composite holds a state, which plain states a composite holds, and which plain state a transition into a composite enters.

**The kernel.** It runs the flat machine. A composite never changes which step commits, so the law proof, Simulate, the oracle and the built app are unchanged, and a test shows the law proof finds the same runs with and without the grouping.

**SCXML.** A composite becomes a compound `<state>` with its `initial`, holding its children. Where one action leaves every state inside a composite (ADR-0232 makes those transitions alike but for their source), the chart carries that transition once, on the composite, so the engine's own hierarchy decides it. The outermost composite that fits wins. The differential runs every oracle case on the nested chart and requires the kernel's answer. As a negative control, a chart that carries such an action on an inner composite only disagrees.

**Diagrams.** Mermaid and PlantUML write `state X { ... }` blocks, and DOT nests clusters. PlayIDE draws a box around each composite's states, and its layout keeps them together (dagre's compound graphs, MIT). A flat model is laid out exactly as before. The diff reports composites added, removed or regrouped.

**Edits.** Renaming a state renames it in its composite. Removing a state takes it out of its composite, but a state that is a composite's initial child or its only child is still in use.

**Interchange.** The UML exports list composites as not carried, as they do for value guards and time events.

**The example.** The refund desk groups `AwaitingApproval` and `WithSupervisor` as `Deciding`, and `Approved` and `PayoutFailed` as `PayingOut`.

### Consequences

* Good: a large machine reads as a few boxes, and the grouping is part of the model rather than a drawing.
* Good: an independent SCXML engine runs the hierarchy and agrees with the flat kernel on every case.
* Bad: no orthogonal regions and no history states.
* Bad: a transition from a composite is stored as one transition per state inside it. PlayIDE has no single edit that adds them all yet.
* Bad: the UML files do not carry composites yet.
* Revisit when: a pack needs parallel regions or history, or PlayIDE needs to group and ungroup states as an edit.
