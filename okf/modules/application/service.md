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
  sha256: 3c519b7d915b8aed49cfeab5e71ffbcde6a6c1ff29d1be83b36629a60fdb7580
notes_baseline: ae7fdf99d2bda4c2ddc81fad14638a3c56e955d23fca7b81cb361bfb322a1b30
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
* [`application/edit_preview`](/modules/application/edit_preview.md)
* [`application/edit_proposal`](/modules/application/edit_proposal.md)
* [`application/formal`](/modules/application/formal.md)
* [`application/generated_app`](/modules/application/generated_app.md)
* [`application/history`](/modules/application/history.md)
* [`application/owner_plan`](/modules/application/owner_plan.md)
* [`application/ports`](/modules/application/ports.md)
* [`application/repository`](/modules/application/repository.md)
* [`application/runtime`](/modules/application/runtime.md)
* [`application/service_views`](/modules/application/service_views.md)
* [`application/verifier`](/modules/application/verifier.md)
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
* [application.edit_preview](/modules/application/edit_preview.md) - Read-only edit projection over one captured case, using the same interpreter as owner edits.
* [application.edit_proposal](/modules/application/edit_proposal.md) - A read-only offline proposal over one captured candidate; owner edits keep their existing boundary.
* [application.formal](/modules/application/formal.md) - Formal evidence in the application layer: seal what an adapter collected, and build the packet view.
* [application.generated_app](/modules/application/generated_app.md) - Shared generation and exact-app evidence operations for the existing kernel and checker.
* [application.history](/modules/application/history.md) - Semantic history is a projection of typed commands, replayed by the existing policy interpreter.
* [application.owner_plan](/modules/application/owner_plan.md) - Exact owner-plan case construction; authority and atomic storage remain in Studio.
* [application.ports](/modules/application/ports.md) - Application-owned ports.
* [application.repository](/modules/application/repository.md) - Read-only repository evidence port; this does not grant project execution or approval.
* [application.runtime](/modules/application/runtime.md) - Generic execution algorithm; the domain (policy, laws, typed effects) comes from the pack.
* [application.service_views](/modules/application/service_views.md) - Read-only Studio projections over the same case, pack and exact-app evidence.
* [application.verifier](/modules/application/verifier.md) - Bounded synthetic runtime experiments.
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
* [application.service.Studio.apply](/symbols/application/service/Studio.apply.md) - `def apply(self, case_id: str, expected: int, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.approve](/symbols/application/service/Studio.approve.md) - `def approve(self, case_id: str, expected: int, subject_hash: str, answers: dict[str, str], acknowledge_unknow…` in `application/service`.
* [application.service.Studio.create](/symbols/application/service/Studio.create.md) - `def create(self, request: str) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.discard](/symbols/application/service/Studio.discard.md) - `def discard(self, case_id: str, expected: int) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.edit](/symbols/application/service/Studio.edit.md) - `def edit(self, case_id: str, expected: int, tx: Transaction, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.edit_preview](/symbols/application/service/Studio.edit_preview.md) - Read-only edit preview bound to one case snapshot; the owner edit still requires capability and CAS.
* [application.service.Studio.execute](/symbols/application/service/Studio.execute.md) - `def execute(self, case_id: str, command: ExecuteCommand, fault: Callable[[str], None] | None=None) -> dict[st…` in `application/service`.
* [application.service.Studio.formal_view](/symbols/application/service/Studio.formal_view.md) - Formal evidence for a bare workflow (``eija compile``): collected and sealed in memory, never stored, never a decision.
* [application.service.Studio.from_plan](/symbols/application/service/Studio.from_plan.md) - Select an exact owner-reviewed command batch; previews and provenance never grant authority.
* [application.service.Studio.layout](/symbols/application/service/Studio.layout.md) - `def layout(self, case_id: str, expected: int, change: LayoutChange, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio(StudioViews)` in `application/service`.
* [application.service.Studio.propose](/symbols/application/service/Studio.propose.md) - `def propose(self, case_id: str, expected: int, *, consent: bool=False) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.propose_edit](/symbols/application/service/Studio.propose_edit.md) - Read-only offline proposal; capture and recheck the case revision without granting owner authority.
* [application.service.Studio.redo](/symbols/application/service/Studio.redo.md) - Reapply the next undone typed command through the same interpreter and policy checks.
* [application.service.Studio.reset_preview](/symbols/application/service/Studio.reset_preview.md) - `def reset_preview(self, case_id: str, expected: int, state: str | None=None) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.save](/symbols/application/service/Studio.save.md) - `def save(self, case_id: str, expected: int) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.select](/symbols/application/service/Studio.select.md) - `def select(self, case_id: str, expected: int, interpretation: str, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.undo](/symbols/application/service/Studio.undo.md) - Undo the last owner semantic edit; the selected meaning remains an indivisible protected prefix.
* [application.service.Studio.verify](/symbols/application/service/Studio.verify.md) - `def verify(self, case_id: str, expected: int) -> dict[str, Any]` in `application/service`.
* [application.service.now](/symbols/application/service/now.md) - `def now() -> str` in `application/service`.
<!-- okf:generated:end links -->
