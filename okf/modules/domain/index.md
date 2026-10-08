# Domain layer: contracts, protected policy, impact closure and evidence assessment

# Modules

* [domain.affordance](affordance.md) - Affordance map (WBS 1.3): which single edits the kernel would accept, and why the others are refused.
* [domain.change_case](change_case.md) - Module `domain/change_case` (no module docstring).
* [domain.data](data.md) - The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.
* [domain.evidence](evidence.md) - Compatibility is computed.
* [domain.evidence_kinds](evidence_kinds.md) - The registry of evidence kinds the kernel can assess (ADR-0145).
* [domain.formal](formal.md) - Primitives for per-kind admissibility of formal evidence (ADR-0145, ADR-0146).
* [domain.formal_bend](formal_bend.md) - Admissibility of ``bend_proof`` receipts (ADR-0146; lane bend, ADR-0025 and ADR-0026).
* [domain.formal_bmc](formal_bmc.md) - Admissibility of ``bounded_model_check`` receipts (ADR-0146; lane smt-bmc, ADR-0030).
* [domain.formal_smt](formal_smt.md) - Admissibility of ``smt_proof`` receipts (ADR-0146; lane smt-bmc, ADR-0029).
* [domain.impact](impact.md) - Module `domain/impact` (no module docstring).
* [domain.laws](laws.md) - Typed law DSL of a domain pack: what a workflow may never do, stated as data (WBS 1.1/1.2).
* [domain.models](models.md) - Module `domain/models` (no module docstring).
* [domain.pack](pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.policy](policy.md) - Generic policy: coherence with a domain pack's declared action catalog, the pack's laws, and declared effects.
* [domain.screens](screens.md) - Screens: the user interface of a pack's app, designed against its use cases and data model (ADR-0154).
* [domain.sequences](sequences.md) - Sequences: UML interactions between the pack's actors and its records, kept beside the pack (ADR-0185).
* [domain.transactions](transactions.md) - Open change vocabulary (WBS 1.3): the semantic edits an owner (or a pack meaning) may make to a workflow.
