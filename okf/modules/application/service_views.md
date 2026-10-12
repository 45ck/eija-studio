---
type: Module
title: application.service_views
description: Read-only Studio projections over the same case, pack and exact-app evidence.
resource: repo://src/eija_studio/application/service_views.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service_views.py
  title: application/service_views.py
  hash_method: ast-api-v1
  sha256: e61b50e283200bc62161b2d63f300ba2a169680ddf8739fbfc5fb0fae6339195
notes_baseline: 83f9db46bd368eaa37aca80e51017729c5e3e9c164ab1344875eb4c61c0f660d
verified:
- by: process:playide-service-cohesion
  at: '2026-10-12T05:30:41Z'
  notes_sha256: 6bd945bb2661744dfe1b774608c855971a0b436bea21f026946dfc61868878aa
  sources_sha256: 83f9db46bd368eaa37aca80e51017729c5e3e9c164ab1344875eb4c61c0f660d
---

# application.service_views

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/service_views.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Read-only Studio projections over the same case, pack and exact-app evidence.

The command service owns authority, signed decisions and all writes. These inherited
views preserve its public API while keeping projections and source navigation together.
~~~

## Public symbols

* [`StudioViews`](/symbols/application/service_views/StudioViews.md) (class) - Projection half of Studio; callbacks use the command service's case and review checks.

## Internal imports

* [`application/formal`](/modules/application/formal.md)
* [`application/history`](/modules/application/history.md)
* [`application/ports`](/modules/application/ports.md)
* [`application/repository`](/modules/application/repository.md)
* [`domain/affordance`](/modules/domain/affordance.md)
* [`domain/change_case`](/modules/domain/change_case.md)
* [`domain/generated_app`](/modules/domain/generated_app.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/policy`](/modules/domain/policy.md)
* [`domain/transactions`](/modules/domain/transactions.md)
<!-- okf:generated:end facts -->

## Notes

This module groups Studio's read-only workbench, repository, model/history, review and activation projections. The inherited methods operate on the same configured ports and cases as Studio; no second model, interpreter, owner capability or persistence service is introduced.

Reads retain their transaction scopes. `active_app_build` loads the recorded association and originating applied case, remeasures the review packet outside that read transaction, then rereads the active record before reporting current freshness. `build_approval` requires an exact subject match. Neither method writes an approval or activates a model.

Read-only means no case, baseline or audit mutation here. A view may inspect stored artifacts or call Studio's formal-evidence projection, which can seal observations in memory without persisting a decision. Repository text stays bounded to the existing configured read ports.

Inherited methods now have source definitions in this module. Old Studio method pages remain deprecated history; neither inheritance nor a current code link proves model/implementation fidelity. Command bindings remain in Studio and behavioral checks must exercise the concrete service.

<!-- okf:generated:begin links -->
## Imports

* [application.formal](/modules/application/formal.md) - Formal evidence in the application layer: seal what an adapter collected, and build the packet view.
* [application.history](/modules/application/history.md) - Semantic history is a projection of typed commands, replayed by the existing policy interpreter.
* [application.ports](/modules/application/ports.md) - Application-owned ports.
* [application.repository](/modules/application/repository.md) - Read-only repository evidence port; this does not grant project execution or approval.
* [domain.affordance](/modules/domain/affordance.md) - Affordance map (WBS 1.3): which single edits the kernel would accept, and why the others are refused.
* [domain.change_case](/modules/domain/change_case.md) - Module `domain/change_case` (no module docstring).
* [domain.generated_app](/modules/domain/generated_app.md) - Versioned exact generated-app selection and evidence contracts; no authority is implied by a hash.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.policy](/modules/domain/policy.md) - Generic policy: coherence with a domain pack's declared action catalog, the pack's laws, and declared effects.
* [domain.transactions](/modules/domain/transactions.md) - Open change vocabulary (WBS 1.3): the semantic edits an owner (or a pack meaning) may make to a workflow.

## Referenced by

* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
* [application.service_views.StudioViews.active_app_build](/symbols/application/service_views/StudioViews.active_app_build.md) - Read the atomically associated case and remeasure its exact approved generated application.
* [application.service_views.StudioViews.affordances](/symbols/application/service_views/StudioViews.affordances.md) - Which single edits of the case's working model the kernel would accept (read-only).
* [application.service_views.StudioViews.build_approval](/symbols/application/service_views/StudioViews.build_approval.md) - An unreviewed preview may run, but cannot inherit approval from a matching workflow alone.
* [application.service_views.StudioViews.edit_check](/symbols/application/service_views/StudioViews.edit_check.md) - Dry-run one edit: {legal, codes, refs}.
* [application.service_views.StudioViews.export](/symbols/application/service_views/StudioViews.export.md) - `def export(self, case_id: str) -> dict[str, Any]` in `application/service_views`.
* [application.service_views.StudioViews.formal_view](/symbols/application/service_views/StudioViews.formal_view.md) - `def formal_view(self, model: Workflow) -> dict[str, Any]` in `application/service_views`.
* [application.service_views.StudioViews.history](/symbols/application/service_views/StudioViews.history.md) - Reconstructed semantic revisions and append-only command audit; never changes the case.
* [application.service_views.StudioViews](/symbols/application/service_views/StudioViews.md) - Projection half of Studio; callbacks use the command service's case and review checks.
* [application.service_views.StudioViews.repository_change](/symbols/application/service_views/StudioViews.repository_change.md) - Compare immutable source revisions; this grants no model or repository write authority.
* [application.service_views.StudioViews.repository_change_file](/symbols/application/service_views/StudioViews.repository_change_file.md) - Read bounded historical text and syntax; live source identity remains separate.
* [application.service_views.StudioViews.repository_freshness](/symbols/application/service_views/StudioViews.repository_freshness.md) - Observe captured byte identity; this grants no source conformance, evidence or owner authority.
* [application.service_views.StudioViews.repository_impact](/symbols/application/service_views/StudioViews.repository_impact.md) - Known repository links only.
* [application.service_views.StudioViews.repository_source](/symbols/application/service_views/StudioViews.repository_source.md) - Bounded source view from the configured repository's captured nodes; no arbitrary path or execution.
* [application.service_views.StudioViews.view](/symbols/application/service_views/StudioViews.view.md) - `def view(self, case_id: str, scope: str='local-demo') -> dict[str, Any]` in `application/service_views`.
* [application.service_views.StudioViews.workbench](/symbols/application/service_views/StudioViews.workbench.md) - Current pack declarations and baseline, with separately labelled read-only repository facts.
* [application.service_views.StudioViews.workflows](/symbols/application/service_views/StudioViews.workflows.md) - Baseline and candidate of a case, for read-only projections (diagrams).
<!-- okf:generated:end links -->
