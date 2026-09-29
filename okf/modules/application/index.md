# Application layer: runtime, verifier, compiler, ports and the Studio use cases

# Modules

* [application.compiler](compiler.md) - Compiler: model → projections + impacts + obligations + computed review packet.
* [application.diagram_catalog](diagram_catalog.md) - Named diagram views over a baseline and an optional candidate Workflow.
* [application.diagram_emitters](diagram_emitters.md) - Text emitters for the diagram models in `application.diagrams`: Mermaid, PlantUML and Graphviz DOT.
* [application.diagrams](diagrams.md) - Diagram models derived from the executable Workflow (ADR-0019, ADR-0023).
* [application.formal](formal.md) - Formal evidence in the application layer: seal what an adapter collected, and build the packet view.
* [application.ports](ports.md) - Application-owned ports.
* [application.runtime](runtime.md) - Generic execution algorithm; the domain (policy, laws, typed effects) comes from the pack.
* [application.service](service.md) - Module `application/service` (no module docstring).
* [application.verifier](verifier.md) - Bounded synthetic runtime experiments.
