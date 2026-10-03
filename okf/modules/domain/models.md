---
type: Module
title: domain.models
description: Module `domain/models` (no module docstring).
resource: repo://src/eija_studio/domain/models.py
tags:
- module
- domain
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py
  title: domain/models.py
  hash_method: ast-api-v1
  sha256: 19ee9ee062677e926136fd9126481b5f144184375dc48ef9f27ddae7c4e63a95
notes_baseline: 61c6c34f6e7082be87df3327b8157143fce5f509c507cb33393ee174af67909e
---

# domain.models

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | domain |
| Code | `repo://src/eija_studio/domain/models.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

_The source carries no module docstring._

## Public symbols

* [`AGENT`](/symbols/domain/models/AGENT.md) (constant) - no docstring
* [`Alternative`](/symbols/domain/models/Alternative.md) (class) - no docstring
* [`BASE_GUARDS`](/symbols/domain/models/BASE_GUARDS.md) (constant) - no docstring
* [`Contract`](/symbols/domain/models/Contract.md) (class) - no docstring
* [`DomainError`](/symbols/domain/models/DomainError.md) (class) - Stable error code: never expose provider secrets or arbitrary exception text.
* [`ExecuteCommand`](/symbols/domain/models/ExecuteCommand.md) (class) - no docstring
* [`Guard`](/symbols/domain/models/Guard.md) (type-alias) - no docstring
* [`LayoutChange`](/symbols/domain/models/LayoutChange.md) (class) - no docstring
* [`MEANING_ID`](/symbols/domain/models/MEANING_ID.md) (constant) - no docstring
* [`OWNER`](/symbols/domain/models/OWNER.md) (constant) - no docstring
* [`Principal`](/symbols/domain/models/Principal.md) (class) - no docstring
* [`Proposal`](/symbols/domain/models/Proposal.md) (class) - no docstring
* [`SemanticTransaction`](/symbols/domain/models/SemanticTransaction.md) (class) - DEPRECATED closed vocabulary, superseded by the open one in ``domain.transactions`` (WBS 1.3).
* [`Transition`](/symbols/domain/models/Transition.md) (class) - no docstring
* [`Workflow`](/symbols/domain/models/Workflow.md) (class) - no docstring
* [`canonical`](/symbols/domain/models/canonical.md) (function) - no docstring
* [`fingerprint`](/symbols/domain/models/fingerprint.md) (function) - no docstring
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [Governance](/contexts/governance.md) - Owns Local capabilities, exact-revision acknowledgement, active baseline version
* [adapters.edit_proposals](/modules/adapters/edit_proposals.md) - Bounded offline request fixture: exact model names and complete phrases, never an LLM.
* [adapters.identity](/modules/adapters/identity.md) - Measured release identity, not a proof of correctness or author authenticity.
* [adapters.receipts](/modules/adapters/receipts.md) - Local integrity seal.
* [adapters.repository](/modules/adapters/repository.md) - Repository analysis and bounded source navigation over captured checkout bytes.
* [adapters.repository_capture](/modules/adapters/repository_capture.md) - Bounded repository reads adapted to the existing deterministic Weave engine.
* [adapters.repository_change_snapshot](/modules/adapters/repository_change_snapshot.md) - Captured immutable comparison snapshots shared by capture, analysis and retention.
* [adapters.repository_changes](/modules/adapters/repository_changes.md) - Read-only, bounded comparison of two local Git commits.
* [adapters.sqlite_store](/modules/adapters/sqlite_store.md) - Durable local unit of work.
* [application.compiler](/modules/application/compiler.md) - Compiler: model → projections + impacts + obligations + computed review packet.
* [application.diagram_catalog](/modules/application/diagram_catalog.md) - Named diagram views over a baseline and an optional candidate Workflow.
* [application.diagram_emitters](/modules/application/diagram_emitters.md) - Text emitters for the diagram models in `application.diagrams`: Mermaid, PlantUML and Graphviz DOT.
* [application.diagrams](/modules/application/diagrams.md) - Diagram models derived from the executable Workflow (ADR-0019, ADR-0023).
* [application.edit_preview](/modules/application/edit_preview.md) - Read-only edit projection over one captured case, using the same interpreter as owner edits.
* [application.edit_proposal](/modules/application/edit_proposal.md) - A read-only offline proposal over one captured candidate; owner edits keep their existing boundary.
* [application.formal](/modules/application/formal.md) - Formal evidence in the application layer: seal what an adapter collected, and build the packet view.
* [application.history](/modules/application/history.md) - Semantic history is a projection of typed commands, replayed by the existing policy interpreter.
* [application.ports](/modules/application/ports.md) - Application-owned ports.
* [application.repository](/modules/application/repository.md) - Read-only repository evidence port; this does not grant project execution or approval.
* [application.runtime](/modules/application/runtime.md) - Generic execution algorithm; the domain (policy, laws, typed effects) comes from the pack.
* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
* [application.verifier](/modules/application/verifier.md) - Bounded synthetic runtime experiments.
* [application.witness_inspection](/modules/application/witness_inspection.md) - Immutable display projections of the deciding formal record, never new evidence or verdicts.
* [domain.affordance](/modules/domain/affordance.md) - Affordance map (WBS 1.3): which single edits the kernel would accept, and why the others are refused.
* [domain.change_case](/modules/domain/change_case.md) - Module `domain/change_case` (no module docstring).
* [domain.evidence](/modules/domain/evidence.md) - Compatibility is computed.
* [domain.impact](/modules/domain/impact.md) - Module `domain/impact` (no module docstring).
* [domain.laws](/modules/domain/laws.md) - Typed law DSL of a domain pack: what a workflow may never do, stated as data (WBS 1.1/1.2).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.policy](/modules/domain/policy.md) - Generic policy: coherence with a domain pack's declared action catalog, the pack's laws, and declared effects.
* [domain.transactions](/modules/domain/transactions.md) - Open change vocabulary (WBS 1.3): the semantic edits an owner (or a pack meaning) may make to a workflow.
* [interfaces.agent_config](/modules/interfaces/agent_config.md) - Copy-paste MCP client configuration for `eija mcp --print-config <client>`.
* [interfaces.cli](/modules/interfaces/cli.md) - Module `interfaces/cli` (no module docstring).
* [interfaces.http](/modules/interfaces/http.md) - Loopback-only local adapter.
* [interfaces.mcp_server](/modules/interfaces/mcp_server.md) - MCP (Model Context Protocol) adapter: the agent-facing face of EIJA Studio.
* [domain.models.AGENT](/symbols/domain/models/AGENT.md) - Constant `AGENT` in `domain/models`.
* [domain.models.Alternative](/symbols/domain/models/Alternative.md) - `class Alternative(Contract)` in `domain/models`.
* [domain.models.BASE_GUARDS](/symbols/domain/models/BASE_GUARDS.md) - Constant `BASE_GUARDS` in `domain/models`.
* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.ExecuteCommand](/symbols/domain/models/ExecuteCommand.md) - `class ExecuteCommand(Contract)` in `domain/models`.
* [domain.models.Guard](/symbols/domain/models/Guard.md) - Type alias `Guard` in `domain/models`.
* [domain.models.LayoutChange](/symbols/domain/models/LayoutChange.md) - `class LayoutChange(Contract)` in `domain/models`.
* [domain.models.MEANING_ID](/symbols/domain/models/MEANING_ID.md) - Constant `MEANING_ID` in `domain/models`.
* [domain.models.OWNER](/symbols/domain/models/OWNER.md) - Constant `OWNER` in `domain/models`.
* [domain.models.Principal](/symbols/domain/models/Principal.md) - `class Principal(Contract)` in `domain/models`.
* [domain.models.Principal.require](/symbols/domain/models/Principal.require.md) - `def require(self, capability: str) -> None` in `domain/models`.
* [domain.models.Proposal](/symbols/domain/models/Proposal.md) - `class Proposal(Contract)` in `domain/models`.
* [domain.models.Proposal.unique](/symbols/domain/models/Proposal.unique.md) - `def unique(self) -> Proposal` in `domain/models`.
* [domain.models.SemanticTransaction](/symbols/domain/models/SemanticTransaction.md) - DEPRECATED closed vocabulary, superseded by the open one in ``domain.transactions`` (WBS 1.3).
* [domain.models.Transition.guarded](/symbols/domain/models/Transition.guarded.md) - `def guarded(self) -> Transition` in `domain/models`.
* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models`.
* [domain.models.Workflow.coherent](/symbols/domain/models/Workflow.coherent.md) - `def coherent(self) -> Workflow` in `domain/models`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.models.Workflow.semantic_hash](/symbols/domain/models/Workflow.semantic_hash.md) - `def semantic_hash(self) -> str` in `domain/models`.
* [domain.models.canonical](/symbols/domain/models/canonical.md) - `def canonical(value: Any) -> str` in `domain/models`.
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models`.
<!-- okf:generated:end links -->
