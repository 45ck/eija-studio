---
type: Class
title: application.service_views.StudioViews
description: Projection half of Studio; callbacks use the command service's case and review checks.
resource: repo://src/eija_studio/application/service_views.py#StudioViews
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service_views.py#StudioViews
  title: application/service_views.py
  hash_method: ast-sig-v1
  sha256: 4a82b73f79b217c8f60c1c7f4e156dc55123aa9aee84460c237548b5c38ad5e9
notes_baseline: 161b07a8295fe61d0001659c8b2b3ac34d9976e508984e5ebee49cc06602ad70
verified:
- by: process:playide-service-cohesion
  at: '2026-10-12T05:30:41Z'
  notes_sha256: bd64e3f7e5999b91e18e641fe8e17afc20744e1bf5527c2bff0ab9fad268aeb7
  sources_sha256: 161b07a8295fe61d0001659c8b2b3ac34d9976e508984e5ebee49cc06602ad70
---

# application.service_views.StudioViews

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/service_views`](/modules/application/service_views.md) |
| Signature | `class StudioViews(ABC)` |
| Code | `repo://src/eija_studio/application/service_views.py#StudioViews` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Projection half of Studio; callbacks use the command service's case and review checks.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `store` | `Repository` |  |
| `pack` | `Pack` |  |
| `formal` | `FormalEvidenceSource \| None` |  |
| `identity_provider` | `IdentityProvider` |  |
| `repository` | `RepositorySource \| None` |  |
| `repository_changes` | `RepositoryChangeSource \| None` |  |
| `signer` | `ReceiptAuthenticator` |  |

## Methods

* [`active_app_build`](/symbols/application/service_views/StudioViews.active_app_build.md) - `def active_app_build(self, active: dict[str, Any] \| None=None) -> dict[str, Any] \| None`
* [`affordances`](/symbols/application/service_views/StudioViews.affordances.md) - `def affordances(self, case_id: str) -> dict[str, Any]`
* [`build_approval`](/symbols/application/service_views/StudioViews.build_approval.md) - `def build_approval(self, subject: dict[str, Any]) -> dict[str, Any]`
* [`edit_check`](/symbols/application/service_views/StudioViews.edit_check.md) - `def edit_check(self, case_id: str, tx: Transaction) -> dict[str, Any]`
* [`export`](/symbols/application/service_views/StudioViews.export.md) - `def export(self, case_id: str) -> dict[str, Any]`
* [`formal_view`](/symbols/application/service_views/StudioViews.formal_view.md) - `def formal_view(self, model: Workflow) -> dict[str, Any]`
* [`history`](/symbols/application/service_views/StudioViews.history.md) - `def history(self, case_id: str) -> dict[str, Any]`
* [`repository_change`](/symbols/application/service_views/StudioViews.repository_change.md) - `def repository_change(self, base: str, head: str) -> dict[str, Any]`
* [`repository_change_file`](/symbols/application/service_views/StudioViews.repository_change_file.md) - `def repository_change_file(self, base: str, head: str, path: str, reference: str \| None=None) -> dict[str, Any]`
* [`repository_freshness`](/symbols/application/service_views/StudioViews.repository_freshness.md) - `def repository_freshness(self, expected_source_hash: str) -> dict[str, Any]`
* [`repository_impact`](/symbols/application/service_views/StudioViews.repository_impact.md) - `def repository_impact(self, term: str, *, expected_source_hash: str \| None=None) -> dict[str, Any]`
* [`repository_source`](/symbols/application/service_views/StudioViews.repository_source.md) - `def repository_source(self, reference: str, *, expected_source_hash: str \| None=None) -> dict[str, Any]`
* [`view`](/symbols/application/service_views/StudioViews.view.md) - `def view(self, case_id: str, scope: str='local-demo') -> dict[str, Any]`
* [`workbench`](/symbols/application/service_views/StudioViews.workbench.md) - `def workbench(self) -> dict[str, Any]`
* [`workflows`](/symbols/application/service_views/StudioViews.workflows.md) - `def workflows(self, case_id: str) -> tuple[Workflow, Workflow \| None]`
<!-- okf:generated:end facts -->

## Notes

StudioViews is the abstract projection part of [Studio](/symbols/application/service/Studio.md), not a standalone authority service. Studio supplies `_case`, `_compile`, `_decision_matches` and `formal_view`; these callbacks reuse its existing case validation, receipt policy, signed decision matching and formal projection.

Its fourteen concrete public views retain their Studio call signatures and make no case, active-model or audit writes. `formal_view` in the generated table is an abstract callback contract; the concrete implementation remains in Studio. Fresh activation badges still require the recorded applied case, matching model/binding, authentic current decision, eligible packet and a second active-record read.

The class page hashes fields and public signatures, not method bodies, inherited dispatch or adapter behavior. Use the method pages and actual concrete-service observations to inspect those boundaries. A process review of this page grants no source approval, owner authority or runtime evidence.

<!-- okf:generated:begin links -->
## Depends on

* [application.ports.FormalEvidenceSource](/symbols/application/ports/FormalEvidenceSource.md) - Where formal artifacts come from (Docker, Java, z3 or saved reports are adapter prerequisites).
* [application.ports.IdentityProvider](/symbols/application/ports/IdentityProvider.md) - Type alias `IdentityProvider` in `application/ports`.
* [application.ports.ReceiptAuthenticator](/symbols/application/ports/ReceiptAuthenticator.md) - `class ReceiptAuthenticator(Protocol)` in `application/ports`.
* [application.ports.Repository](/symbols/application/ports/Repository.md) - `class Repository(Protocol)` in `application/ports`.
* [application.repository.RepositoryChangeSource](/symbols/application/repository/RepositoryChangeSource.md) - Immutable, read-only facts for an explicit pair in one configured repository.
* [application.repository.RepositorySource](/symbols/application/repository/RepositorySource.md) - Evidence about one explicitly configured checkout and its declared domain bindings.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.

## Referenced by

* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio(StudioViews)` in `application/service`.
* [application.service_views.StudioViews.active_app_build](/symbols/application/service_views/StudioViews.active_app_build.md) - Read the atomically associated case and remeasure its exact approved generated application.
* [application.service_views.StudioViews.affordances](/symbols/application/service_views/StudioViews.affordances.md) - Which single edits of the case's working model the kernel would accept (read-only).
* [application.service_views.StudioViews.build_approval](/symbols/application/service_views/StudioViews.build_approval.md) - An unreviewed preview may run, but cannot inherit approval from a matching workflow alone.
* [application.service_views.StudioViews.edit_check](/symbols/application/service_views/StudioViews.edit_check.md) - Dry-run one edit: {legal, codes, refs}.
* [application.service_views.StudioViews.export](/symbols/application/service_views/StudioViews.export.md) - `def export(self, case_id: str) -> dict[str, Any]` in `application/service_views`.
* [application.service_views.StudioViews.formal_view](/symbols/application/service_views/StudioViews.formal_view.md) - `def formal_view(self, model: Workflow) -> dict[str, Any]` in `application/service_views`.
* [application.service_views.StudioViews.history](/symbols/application/service_views/StudioViews.history.md) - Reconstructed semantic revisions and append-only command audit; never changes the case.
* [application.service_views.StudioViews.repository_change](/symbols/application/service_views/StudioViews.repository_change.md) - Compare immutable source revisions; this grants no model or repository write authority.
* [application.service_views.StudioViews.repository_change_file](/symbols/application/service_views/StudioViews.repository_change_file.md) - Read bounded historical text and syntax; live source identity remains separate.
* [application.service_views.StudioViews.repository_freshness](/symbols/application/service_views/StudioViews.repository_freshness.md) - Observe captured byte identity; this grants no source conformance, evidence or owner authority.
* [application.service_views.StudioViews.repository_impact](/symbols/application/service_views/StudioViews.repository_impact.md) - Known repository links only.
* [application.service_views.StudioViews.repository_source](/symbols/application/service_views/StudioViews.repository_source.md) - Bounded source view from the configured repository's captured nodes; no arbitrary path or execution.
* [application.service_views.StudioViews.view](/symbols/application/service_views/StudioViews.view.md) - `def view(self, case_id: str, scope: str='local-demo') -> dict[str, Any]` in `application/service_views`.
* [application.service_views.StudioViews.workbench](/symbols/application/service_views/StudioViews.workbench.md) - Current pack declarations and baseline, with separately labelled read-only repository facts.
* [application.service_views.StudioViews.workflows](/symbols/application/service_views/StudioViews.workflows.md) - Baseline and candidate of a case, for read-only projections (diagrams).
<!-- okf:generated:end links -->
