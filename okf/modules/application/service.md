---
type: Module
title: application.service
description: Module `application/service` (no module docstring).
resource: repo://src/eija_studio/application/service.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py
  title: application/service.py
  hash_method: ast-api-v1
  sha256: 80f7aa453b3255c3949b202f044ca1968d29827b7642fb41dfd7228eee97ccd5
notes_baseline: e9d5a427343d86d166d34a0f32fffa6b4e53bd9bd99161c6344b092839eeca39
---

# application.service

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/service.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

_The source carries no module docstring._

## Public symbols

* [`Studio`](/symbols/application/service/Studio.md) (class) - no docstring
* [`now`](/symbols/application/service/now.md) (function) - no docstring

## Internal imports

* [`application/compiler`](/modules/application/compiler.md)
* [`application/formal`](/modules/application/formal.md)
* [`application/history`](/modules/application/history.md)
* [`application/ports`](/modules/application/ports.md)
* [`application/repository`](/modules/application/repository.md)
* [`application/runtime`](/modules/application/runtime.md)
* [`application/verifier`](/modules/application/verifier.md)
* [`domain/affordance`](/modules/domain/affordance.md)
* [`domain/change_case`](/modules/domain/change_case.md)
* [`domain/formal`](/modules/domain/formal.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/policy`](/modules/domain/policy.md)
* [`domain/transactions`](/modules/domain/transactions.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.compiler](/modules/application/compiler.md) - Compiler: model → projections + impacts + obligations + computed review packet.
* [application.formal](/modules/application/formal.md) - Formal evidence in the application layer: seal what an adapter collected, and build the packet view.
* [application.history](/modules/application/history.md) - Semantic history is a projection of typed commands, replayed by the existing policy interpreter.
* [application.ports](/modules/application/ports.md) - Application-owned ports.
* [application.repository](/modules/application/repository.md) - Read-only repository evidence port; this does not grant project execution or approval.
* [application.runtime](/modules/application/runtime.md) - Generic execution algorithm; the domain (policy, laws, typed effects) comes from the pack.
* [application.verifier](/modules/application/verifier.md) - Bounded synthetic runtime experiments.
* [domain.affordance](/modules/domain/affordance.md) - Affordance map (WBS 1.3): which single edits the kernel would accept, and why the others are refused.
* [domain.change_case](/modules/domain/change_case.md) - Module `domain/change_case` (no module docstring).
* [domain.formal](/modules/domain/formal.md) - Primitives for per-kind admissibility of formal evidence (ADR-0145, ADR-0146).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.policy](/modules/domain/policy.md) - Generic policy: coherence with a domain pack's declared action catalog, the pack's laws, and declared effects.
* [domain.transactions](/modules/domain/transactions.md) - Open change vocabulary (WBS 1.3): the semantic edits an owner (or a pack meaning) may make to a workflow.

## Referenced by

* [Authoring](/contexts/authoring.md) - Owns Requested intent, alternatives, explicit selection, candidate and edits
* [Governance](/contexts/governance.md) - Owns Local capabilities, exact-revision acknowledgement, active baseline version
* [bootstrap](/modules/bootstrap.md) - The only composition root: wires application ports to concrete adapters.
* [interfaces.mcp_server](/modules/interfaces/mcp_server.md) - MCP (Model Context Protocol) adapter: the agent-facing face of EIJA Studio.
* [application.service.Studio.affordances](/symbols/application/service/Studio.affordances.md) - Which single edits of the case's working model the kernel would accept (read-only).
* [application.service.Studio.apply](/symbols/application/service/Studio.apply.md) - `def apply(self, case_id: str, expected: int, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.approve](/symbols/application/service/Studio.approve.md) - `def approve(self, case_id: str, expected: int, subject_hash: str, answers: dict[str, str], acknowledge_unknow…` in `application/service`.
* [application.service.Studio.create](/symbols/application/service/Studio.create.md) - `def create(self, request: str) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.discard](/symbols/application/service/Studio.discard.md) - `def discard(self, case_id: str, expected: int) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.edit](/symbols/application/service/Studio.edit.md) - `def edit(self, case_id: str, expected: int, tx: Transaction, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.edit_check](/symbols/application/service/Studio.edit_check.md) - Dry-run one edit: {legal, codes, refs}.
* [application.service.Studio.execute](/symbols/application/service/Studio.execute.md) - `def execute(self, case_id: str, command: ExecuteCommand, fault: Callable[[str], None] | None=None) -> dict[st…` in `application/service`.
* [application.service.Studio.export](/symbols/application/service/Studio.export.md) - `def export(self, case_id: str) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.formal_view](/symbols/application/service/Studio.formal_view.md) - Formal evidence for a bare workflow (``eija compile``): collected and sealed in memory, never stored, never a decision.
* [application.service.Studio.history](/symbols/application/service/Studio.history.md) - Reconstructed semantic revisions and append-only command audit; never changes the case.
* [application.service.Studio.layout](/symbols/application/service/Studio.layout.md) - `def layout(self, case_id: str, expected: int, change: LayoutChange, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio` in `application/service`.
* [application.service.Studio.propose](/symbols/application/service/Studio.propose.md) - `def propose(self, case_id: str, expected: int, *, consent: bool=False) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.redo](/symbols/application/service/Studio.redo.md) - Reapply the next undone typed command through the same interpreter and policy checks.
* [application.service.Studio.repository_change](/symbols/application/service/Studio.repository_change.md) - Compare immutable source revisions; this grants no model or repository write authority.
* [application.service.Studio.repository_change_file](/symbols/application/service/Studio.repository_change_file.md) - Read bounded historical text and syntax; live source identity remains separate.
* [application.service.Studio.repository_freshness](/symbols/application/service/Studio.repository_freshness.md) - Observe captured byte identity; this grants no source conformance, evidence or owner authority.
* [application.service.Studio.repository_impact](/symbols/application/service/Studio.repository_impact.md) - Known repository links only.
* [application.service.Studio.repository_source](/symbols/application/service/Studio.repository_source.md) - Bounded source view from the configured repository's captured nodes; no arbitrary path or execution.
* [application.service.Studio.reset_preview](/symbols/application/service/Studio.reset_preview.md) - `def reset_preview(self, case_id: str, expected: int, state: str | None=None) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.save](/symbols/application/service/Studio.save.md) - `def save(self, case_id: str, expected: int) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.select](/symbols/application/service/Studio.select.md) - `def select(self, case_id: str, expected: int, interpretation: str, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.undo](/symbols/application/service/Studio.undo.md) - Undo the last owner semantic edit; the selected meaning remains an indivisible protected prefix.
* [application.service.Studio.verify](/symbols/application/service/Studio.verify.md) - `def verify(self, case_id: str, expected: int) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.view](/symbols/application/service/Studio.view.md) - `def view(self, case_id: str, scope: str='local-demo') -> dict[str, Any]` in `application/service`.
* [application.service.Studio.workbench](/symbols/application/service/Studio.workbench.md) - Current pack declarations and baseline, with separately labelled read-only repository facts.
* [application.service.Studio.workflows](/symbols/application/service/Studio.workflows.md) - Baseline and candidate of a case, for read-only projections (diagrams).
* [application.service.now](/symbols/application/service/now.md) - `def now() -> str` in `application/service`.
<!-- okf:generated:end links -->
