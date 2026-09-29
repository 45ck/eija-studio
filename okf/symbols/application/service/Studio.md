---
type: Class
title: application.service.Studio
description: 'The Studio use cases: create, propose, select, edit, verify, approve, apply and execute over a Change Case.'
resource: repo://src/eija_studio/application/service.py#Studio
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio
  title: application/service.py
  hash_method: ast-sig-v1
  sha256: 97daa3703a8b24b448c8b73bc0cf0b3cc09f5c0c3313ff0e1fc2cb3003730100
description_override: 'The Studio use cases: create, propose, select, edit, verify, approve, apply and execute over a Change Case.'
notes_baseline: de7d46763e5f821cd3e3ec357af51a719512db92a36ea21137307c05cc341e97
verified:
- by: process:claude-code-integration-phase0
  at: '2026-09-29T04:30:00Z'
  notes_sha256: d780f3dd51d7e77169dee305e138faf80bb4360a4c2594b58856017214392bdb
  sources_sha256: de7d46763e5f821cd3e3ec357af51a719512db92a36ea21137307c05cc341e97
---

# application.service.Studio

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/service`](/modules/application/service.md) |
| Signature | `class Studio` |
| Code | `repo://src/eija_studio/application/service.py#Studio` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Methods

* [`apply`](/symbols/application/service/Studio.apply.md) - `def apply(self, case_id: str, expected: int, principal: Principal) -> dict[str, Any]`
* [`approve`](/symbols/application/service/Studio.approve.md) - `def approve(self, case_id: str, expected: int, subject_hash: str, answers: dict[str, str], acknowledge_unknowns: bool, principal: Principal, scope: str='local-demo') -> dict[str, Any]`
* [`create`](/symbols/application/service/Studio.create.md) - `def create(self, request: str) -> dict[str, Any]`
* [`discard`](/symbols/application/service/Studio.discard.md) - `def discard(self, case_id: str, expected: int) -> dict[str, Any]`
* [`edit`](/symbols/application/service/Studio.edit.md) - `def edit(self, case_id: str, expected: int, tx: SemanticTransaction, principal: Principal) -> dict[str, Any]`
* [`execute`](/symbols/application/service/Studio.execute.md) - `def execute(self, case_id: str, command: ExecuteCommand, fault: Callable[[str], None] \| None=None) -> dict[str, Any]`
* [`export`](/symbols/application/service/Studio.export.md) - `def export(self, case_id: str) -> dict[str, Any]`
* [`formal_view`](/symbols/application/service/Studio.formal_view.md) - `def formal_view(self, model: Workflow) -> dict[str, Any]`
* [`layout`](/symbols/application/service/Studio.layout.md) - `def layout(self, case_id: str, expected: int, change: LayoutChange, principal: Principal) -> dict[str, Any]`
* [`propose`](/symbols/application/service/Studio.propose.md) - `def propose(self, case_id: str, expected: int, *, consent: bool=False) -> dict[str, Any]`
* [`reset_preview`](/symbols/application/service/Studio.reset_preview.md) - `def reset_preview(self, case_id: str, expected: int, state: str \| None=None) -> dict[str, Any]`
* [`save`](/symbols/application/service/Studio.save.md) - `def save(self, case_id: str, expected: int) -> dict[str, Any]`
* [`select`](/symbols/application/service/Studio.select.md) - `def select(self, case_id: str, expected: int, interpretation: str, principal: Principal) -> dict[str, Any]`
* [`verify`](/symbols/application/service/Studio.verify.md) - `def verify(self, case_id: str, expected: int) -> dict[str, Any]`
* [`view`](/symbols/application/service/Studio.view.md) - `def view(self, case_id: str, scope: str='local-demo') -> dict[str, Any]`
* [`workflows`](/symbols/application/service/Studio.workflows.md) - `def workflows(self, case_id: str) -> tuple[Workflow, Workflow \| None]`
<!-- okf:generated:end facts -->

## Notes

Every mutation runs inside one unit of work with version checks. Governance methods require a [Principal](/symbols/domain/models/Principal.md) capability; verification and approval are separate steps and neither implies apply ([Local Decision](/language/local-decision.md)).

<!-- okf:generated:begin links -->
## Depends on

* [application.ports.FormalEvidenceSource](/symbols/application/ports/FormalEvidenceSource.md) - Where formal artifacts come from (Docker, Java, z3 or saved reports are adapter prerequisites).
* [application.ports.IdentityProvider](/symbols/application/ports/IdentityProvider.md) - Type alias `IdentityProvider` in `application/ports`.
* [application.ports.ProposalProvider](/symbols/application/ports/ProposalProvider.md) - `class ProposalProvider(Protocol)` in `application/ports`.
* [application.ports.ReceiptAuthenticator](/symbols/application/ports/ReceiptAuthenticator.md) - `class ReceiptAuthenticator(Protocol)` in `application/ports`.
* [application.ports.Repository](/symbols/application/ports/Repository.md) - `class Repository(Protocol)` in `application/ports`.
* [application.ports.SandboxFactory](/symbols/application/ports/SandboxFactory.md) - Type alias `SandboxFactory` in `application/ports`.
* [domain.models.ExecuteCommand](/symbols/domain/models/ExecuteCommand.md) - `class ExecuteCommand(Contract)` in `domain/models`.
* [domain.models.LayoutChange](/symbols/domain/models/LayoutChange.md) - `class LayoutChange(Contract)` in `domain/models`.
* [domain.models.Principal](/symbols/domain/models/Principal.md) - `class Principal(Contract)` in `domain/models`.
* [domain.models.SemanticTransaction](/symbols/domain/models/SemanticTransaction.md) - `class SemanticTransaction(Contract)` in `domain/models`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [application.service.Studio.apply](/symbols/application/service/Studio.apply.md) - `def apply(self, case_id: str, expected: int, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.approve](/symbols/application/service/Studio.approve.md) - `def approve(self, case_id: str, expected: int, subject_hash: str, answers: dict[str, str], acknowledge_unknow…` in `application/service`.
* [application.service.Studio.create](/symbols/application/service/Studio.create.md) - `def create(self, request: str) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.discard](/symbols/application/service/Studio.discard.md) - `def discard(self, case_id: str, expected: int) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.edit](/symbols/application/service/Studio.edit.md) - `def edit(self, case_id: str, expected: int, tx: SemanticTransaction, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.execute](/symbols/application/service/Studio.execute.md) - `def execute(self, case_id: str, command: ExecuteCommand, fault: Callable[[str], None] | None=None) -> dict[st…` in `application/service`.
* [application.service.Studio.export](/symbols/application/service/Studio.export.md) - `def export(self, case_id: str) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.formal_view](/symbols/application/service/Studio.formal_view.md) - Formal evidence for a bare workflow (``eija compile``): collected and sealed in memory, never stored, never a decision.
* [application.service.Studio.layout](/symbols/application/service/Studio.layout.md) - `def layout(self, case_id: str, expected: int, change: LayoutChange, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.propose](/symbols/application/service/Studio.propose.md) - `def propose(self, case_id: str, expected: int, *, consent: bool=False) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.reset_preview](/symbols/application/service/Studio.reset_preview.md) - `def reset_preview(self, case_id: str, expected: int, state: str | None=None) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.save](/symbols/application/service/Studio.save.md) - `def save(self, case_id: str, expected: int) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.select](/symbols/application/service/Studio.select.md) - `def select(self, case_id: str, expected: int, interpretation: str, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.verify](/symbols/application/service/Studio.verify.md) - `def verify(self, case_id: str, expected: int) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.view](/symbols/application/service/Studio.view.md) - `def view(self, case_id: str, scope: str='local-demo') -> dict[str, Any]` in `application/service`.
* [application.service.Studio.workflows](/symbols/application/service/Studio.workflows.md) - Baseline and candidate of a case, for read-only projections (diagrams).
<!-- okf:generated:end links -->
