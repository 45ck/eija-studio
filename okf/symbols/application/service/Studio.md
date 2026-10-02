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
  sha256: 82e069eec049dac30908556b342ee1216b85070100377baa66ab7ef861c4b151
description_override: 'The Studio use cases: create, propose, select, edit, verify, approve, apply and execute over a Change Case.'
notes_baseline: a4a37d1c16da3a06c765472baba47c5c3b13e9b707e3fcbf8f262bc4335f334b
verified:
- by: process:claude-code-integration-phase0
  at: '2026-09-29T04:30:00Z'
  notes_sha256: d780f3dd51d7e77169dee305e138faf80bb4360a4c2594b58856017214392bdb
  sources_sha256: de7d46763e5f821cd3e3ec357af51a719512db92a36ea21137307c05cc341e97
- by: process:eija-wbs-1.3-agent
  at: '2026-09-29T08:20:47Z'
  notes_sha256: d780f3dd51d7e77169dee305e138faf80bb4360a4c2594b58856017214392bdb
  sources_sha256: 4f1379e816c3db01e064ea1774ef7e83c46d346fc9b7858122a08feecd7f7f2e
- by: process:codex-self-dogfood
  at: '2026-10-02T04:33:54Z'
  notes_sha256: 26c4b5cbf900e43a57627ae6075dc53ebea1fefb4efd8227fa8469adda531127
  sources_sha256: cfe3a845cd089e70d754fb5fcbbc3e47df7e03d4c63a1bd47bf7062734b290bd
- by: process:codex-ide-integration
  at: '2026-10-02T05:15:30Z'
  notes_sha256: 62abfebc9050ce78dc72bca0ce8709f948bb279a3ae739fb3ead2be83da4a912
  sources_sha256: 3df72f8f0cc5aaff4076130e21ce81c50640f9a33e0aee011b83899f9cfe5c12
- by: process:codex-review-workspace
  at: '2026-10-02T11:59:23Z'
  notes_sha256: eb4ee7ae00fac76291bc2df9e7edbd3b30b736c73ba5e8135bf53c76b1da40e9
  sources_sha256: 25f65b9ec4658d4094bf6f55fbb251e17a468c9995de8d373b45b6b004570a5c
- by: process:codex-immutable-code-review
  at: '2026-10-02T13:05:54Z'
  notes_sha256: 5c65b08b05d0cc7eb7aa9ed783df92f6d4e99d4fc600f810506a434289cbba7d
  sources_sha256: 19810e6ec12909e2564fed479dc296c3d64c9e51ba1f69d169b250d46711b528
- by: process:codex-edit-preview
  at: '2026-10-02T19:25:25Z'
  notes_sha256: f4a02da478c415d5bda1e511a72b5f08b82df701d0844c29c022945ae8819f8d
  sources_sha256: a4a37d1c16da3a06c765472baba47c5c3b13e9b707e3fcbf8f262bc4335f334b
- by: process:codex-query-cohesion
  at: '2026-10-03T10:00:00+11:00'
  notes_sha256: f4a02da478c415d5bda1e511a72b5f08b82df701d0844c29c022945ae8819f8d
  sources_sha256: a4a37d1c16da3a06c765472baba47c5c3b13e9b707e3fcbf8f262bc4335f334b
- by: process:codex-query-cohesion
  at: '2026-10-02T20:26:56.4586414+00:00'
  notes_sha256: f4a02da478c415d5bda1e511a72b5f08b82df701d0844c29c022945ae8819f8d
  sources_sha256: a4a37d1c16da3a06c765472baba47c5c3b13e9b707e3fcbf8f262bc4335f334b
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

* [`affordances`](/symbols/application/service/Studio.affordances.md) - `def affordances(self, case_id: str) -> dict[str, Any]`
* [`apply`](/symbols/application/service/Studio.apply.md) - `def apply(self, case_id: str, expected: int, principal: Principal) -> dict[str, Any]`
* [`approve`](/symbols/application/service/Studio.approve.md) - `def approve(self, case_id: str, expected: int, subject_hash: str, answers: dict[str, str], acknowledge_unknowns: bool, principal: Principal, scope: str='local-demo') -> dict[str, Any]`
* [`create`](/symbols/application/service/Studio.create.md) - `def create(self, request: str) -> dict[str, Any]`
* [`discard`](/symbols/application/service/Studio.discard.md) - `def discard(self, case_id: str, expected: int) -> dict[str, Any]`
* [`edit`](/symbols/application/service/Studio.edit.md) - `def edit(self, case_id: str, expected: int, tx: Transaction, principal: Principal) -> dict[str, Any]`
* [`edit_check`](/symbols/application/service/Studio.edit_check.md) - `def edit_check(self, case_id: str, tx: Transaction) -> dict[str, Any]`
* [`edit_preview`](/symbols/application/service/Studio.edit_preview.md) - `def edit_preview(self, case_id: str, tx: Transaction) -> dict[str, Any]`
* [`execute`](/symbols/application/service/Studio.execute.md) - `def execute(self, case_id: str, command: ExecuteCommand, fault: Callable[[str], None] \| None=None) -> dict[str, Any]`
* [`export`](/symbols/application/service/Studio.export.md) - `def export(self, case_id: str) -> dict[str, Any]`
* [`formal_view`](/symbols/application/service/Studio.formal_view.md) - `def formal_view(self, model: Workflow) -> dict[str, Any]`
* [`history`](/symbols/application/service/Studio.history.md) - `def history(self, case_id: str) -> dict[str, Any]`
* [`layout`](/symbols/application/service/Studio.layout.md) - `def layout(self, case_id: str, expected: int, change: LayoutChange, principal: Principal) -> dict[str, Any]`
* [`propose`](/symbols/application/service/Studio.propose.md) - `def propose(self, case_id: str, expected: int, *, consent: bool=False) -> dict[str, Any]`
* [`redo`](/symbols/application/service/Studio.redo.md) - `def redo(self, case_id: str, expected: int, principal: Principal) -> dict[str, Any]`
* [`repository_change`](/symbols/application/service/Studio.repository_change.md) - `def repository_change(self, base: str, head: str) -> dict[str, Any]`
* [`repository_change_file`](/symbols/application/service/Studio.repository_change_file.md) - `def repository_change_file(self, base: str, head: str, path: str, reference: str \| None=None) -> dict[str, Any]`
* [`repository_freshness`](/symbols/application/service/Studio.repository_freshness.md) - `def repository_freshness(self, expected_source_hash: str) -> dict[str, Any]`
* [`repository_impact`](/symbols/application/service/Studio.repository_impact.md) - `def repository_impact(self, term: str, *, expected_source_hash: str \| None=None) -> dict[str, Any]`
* [`repository_source`](/symbols/application/service/Studio.repository_source.md) - `def repository_source(self, reference: str, *, expected_source_hash: str \| None=None) -> dict[str, Any]`
* [`reset_preview`](/symbols/application/service/Studio.reset_preview.md) - `def reset_preview(self, case_id: str, expected: int, state: str \| None=None) -> dict[str, Any]`
* [`save`](/symbols/application/service/Studio.save.md) - `def save(self, case_id: str, expected: int) -> dict[str, Any]`
* [`select`](/symbols/application/service/Studio.select.md) - `def select(self, case_id: str, expected: int, interpretation: str, principal: Principal) -> dict[str, Any]`
* [`undo`](/symbols/application/service/Studio.undo.md) - `def undo(self, case_id: str, expected: int, principal: Principal) -> dict[str, Any]`
* [`verify`](/symbols/application/service/Studio.verify.md) - `def verify(self, case_id: str, expected: int) -> dict[str, Any]`
* [`view`](/symbols/application/service/Studio.view.md) - `def view(self, case_id: str, scope: str='local-demo') -> dict[str, Any]`
* [`workbench`](/symbols/application/service/Studio.workbench.md) - `def workbench(self) -> dict[str, Any]`
* [`workflows`](/symbols/application/service/Studio.workflows.md) - `def workflows(self, case_id: str) -> tuple[Workflow, Workflow \| None]`
<!-- okf:generated:end facts -->

## Notes

Every mutation runs inside one unit of work with version checks. Governance methods require a [Principal](/symbols/domain/models/Principal.md) capability; verification and approval are separate steps and neither implies apply ([Local Decision](/language/local-decision.md)).

`workbench` reads pack declarations and the active baseline, alongside an optional
repository snapshot through the application-owned repository port. `repository_impact`
returns the closure of known source links. `repository_source` opens bounded text from
an authorized captured reference. These reads do not edit source, establish
model/implementation equivalence, produce verification receipts or grant owner authority.

Source and impact reads optionally pin a captured source hash. `repository_freshness`
compares that byte identity through the same port; it cannot attest to behavior or
future filesystem state. A stale snapshot must be refreshed before following its
links as though they described the current connection.

`repository_change` and `repository_change_file` use a separate read-only port for
full local Git commit IDs. They retain immutable comparison and changed-file
capture identities, bounded historical source and explicit partial syntax/impact.
These facts neither reuse live source hashes nor establish model conformance,
agent authorship or behavior evidence. An absent port stays unconfigured.

Semantic edit, undo and redo use the existing interpreter with a protected atomic
meaning prefix. They create new case versions, append command provenance and clear
decisions while retaining receipts, baseline and layout. `history` reconstructs
semantic snapshots from commands; it does not invent timestamps for legacy edits.

`edit_check` remains a compact policy-only check against the working model.
`edit_preview` captures one case revision and returns its current model plus the
candidate from the existing interpreter, after the same lifecycle and history
checks as edit. It writes nothing, grants no authority and creates no evidence.
Applying still uses owner edit and the captured case version; an intervening
revision makes that expected version stale.

<!-- okf:generated:begin links -->
## Depends on

* [application.ports.FormalEvidenceSource](/symbols/application/ports/FormalEvidenceSource.md) - Where formal artifacts come from (Docker, Java, z3 or saved reports are adapter prerequisites).
* [application.ports.IdentityProvider](/symbols/application/ports/IdentityProvider.md) - Type alias `IdentityProvider` in `application/ports`.
* [application.ports.ProposalProvider](/symbols/application/ports/ProposalProvider.md) - `class ProposalProvider(Protocol)` in `application/ports`.
* [application.ports.ReceiptAuthenticator](/symbols/application/ports/ReceiptAuthenticator.md) - `class ReceiptAuthenticator(Protocol)` in `application/ports`.
* [application.ports.Repository](/symbols/application/ports/Repository.md) - `class Repository(Protocol)` in `application/ports`.
* [application.ports.SandboxFactory](/symbols/application/ports/SandboxFactory.md) - Type alias `SandboxFactory` in `application/ports`.
* [application.repository.RepositoryChangeSource](/symbols/application/repository/RepositoryChangeSource.md) - Immutable, read-only facts for an explicit pair in one configured repository.
* [application.repository.RepositorySource](/symbols/application/repository/RepositorySource.md) - Evidence about one explicitly configured checkout and its declared domain bindings.
* [domain.models.ExecuteCommand](/symbols/domain/models/ExecuteCommand.md) - `class ExecuteCommand(Contract)` in `domain/models`.
* [domain.models.LayoutChange](/symbols/domain/models/LayoutChange.md) - `class LayoutChange(Contract)` in `domain/models`.
* [domain.models.Principal](/symbols/domain/models/Principal.md) - `class Principal(Contract)` in `domain/models`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.

## Referenced by

* [application.service.Studio.affordances](/symbols/application/service/Studio.affordances.md) - Which single edits of the case's working model the kernel would accept (read-only).
* [application.service.Studio.apply](/symbols/application/service/Studio.apply.md) - `def apply(self, case_id: str, expected: int, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.approve](/symbols/application/service/Studio.approve.md) - `def approve(self, case_id: str, expected: int, subject_hash: str, answers: dict[str, str], acknowledge_unknow…` in `application/service`.
* [application.service.Studio.create](/symbols/application/service/Studio.create.md) - `def create(self, request: str) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.discard](/symbols/application/service/Studio.discard.md) - `def discard(self, case_id: str, expected: int) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.edit](/symbols/application/service/Studio.edit.md) - `def edit(self, case_id: str, expected: int, tx: Transaction, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.edit_check](/symbols/application/service/Studio.edit_check.md) - Dry-run one edit: {legal, codes, refs}.
* [application.service.Studio.edit_preview](/symbols/application/service/Studio.edit_preview.md) - Read-only edit preview bound to one case snapshot; the owner edit still requires capability and CAS.
* [application.service.Studio.execute](/symbols/application/service/Studio.execute.md) - `def execute(self, case_id: str, command: ExecuteCommand, fault: Callable[[str], None] | None=None) -> dict[st…` in `application/service`.
* [application.service.Studio.export](/symbols/application/service/Studio.export.md) - `def export(self, case_id: str) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.formal_view](/symbols/application/service/Studio.formal_view.md) - Formal evidence for a bare workflow (``eija compile``): collected and sealed in memory, never stored, never a decision.
* [application.service.Studio.history](/symbols/application/service/Studio.history.md) - Reconstructed semantic revisions and append-only command audit; never changes the case.
* [application.service.Studio.layout](/symbols/application/service/Studio.layout.md) - `def layout(self, case_id: str, expected: int, change: LayoutChange, principal: Principal) -> dict[str, Any]` in `application/service`.
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
<!-- okf:generated:end links -->
