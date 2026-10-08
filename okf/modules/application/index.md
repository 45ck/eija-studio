# Application layer: runtime, verifier, compiler, ports and the Studio use cases

# Modules

* [application.access](access.md) - Who can do what (ADR-0171): the model's permissions as a role by state matrix, each cell checked by the kernel, and reachability questions such as "can a record reach this state without that role ever acting?".
* [application.appgen](appgen.md) - App generation: a reviewed workflow model becomes a runnable app and its conformance oracle (ADR-0150).
* [application.compiler](compiler.md) - Compiler: model → projections + impacts + obligations + computed review packet.
* [application.components](components.md) - The component diagram of an app built from the model (ADR-0155), extracted from the generated files themselves.
* [application.diagram_catalog](diagram_catalog.md) - Named diagram views over a baseline and an optional candidate Workflow.
* [application.diagram_emitters](diagram_emitters.md) - Text emitters for the diagram models in `application.diagrams`: Mermaid, PlantUML and Graphviz DOT.
* [application.diagrams](diagrams.md) - Diagram models derived from the executable Workflow (ADR-0019, ADR-0023).
* [application.edit_preview](edit_preview.md) - Read-only edit projection over one captured case, using the same interpreter as owner edits.
* [application.edit_proposal](edit_proposal.md) - A read-only offline proposal over one captured candidate; owner edits keep their existing boundary.
* [application.formal](formal.md) - Formal evidence in the application layer: seal what an adapter collected, and build the packet view.
* [application.ghost_diff](ghost_diff.md) - How a change looks on the state machine: both models on one canvas, with nothing hidden (ADR-0176).
* [application.history](history.md) - Semantic history is a projection of typed commands, replayed by the existing policy interpreter.
* [application.law_proof](law_proof.md) - Prove a pack's laws over every run the kernel allows (ADR-0166).
* [application.plan](plan.md) - Plan mode for the PlayIDE chat (ADR-0156): an AI proposes a change as numbered typed steps; the person accepts or rejects each one and sees what the accepted ones would do.
* [application.ports](ports.md) - Application-owned ports.
* [application.repository](repository.md) - Read-only repository evidence port; this does not grant project execution or approval.
* [application.review](review.md) - Review a model change in PlayIDE instead of a pull request (ADR-0175).
* [application.ripple](ripple.md) - Ripple (ADR-0158): what one change to the state machine does to every other diagram of the same system, and the follow-on edits that would keep them in agreement.
* [application.runtime](runtime.md) - Generic execution algorithm; the domain (policy, laws, typed effects) comes from the pack.
* [application.scxml](scxml.md) - The workflow state machine as a W3C SCXML statechart (ADR-0165).
* [application.sequence_layout](sequence_layout.md) - Where a checked sequence is drawn, and its export (ADR-0185).
* [application.sequences](sequences.md) - Sequence diagrams the kernel checks (ADR-0185): can this model produce this interaction?
* [application.service](service.md) - Module `application/service` (no module docstring).
* [application.simulation](simulation.md) - Seeded simulation of people using the app built from a model (ADR-0152).
* [application.verifier](verifier.md) - Bounded synthetic runtime experiments.
* [application.witness_inspection](witness_inspection.md) - Immutable display projections of the deciding formal record, never new evidence or verdicts.
