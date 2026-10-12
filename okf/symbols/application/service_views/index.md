# Symbols of application.service_views

# Classes

* [application.service_views.StudioViews](StudioViews.md) - Projection half of Studio; callbacks use the command service's case and review checks.

# Methods

* [application.service_views.StudioViews.active_app_build](StudioViews.active_app_build.md) - Read the atomically associated case and remeasure its exact approved generated application.
* [application.service_views.StudioViews.affordances](StudioViews.affordances.md) - Which single edits of the case's working model the kernel would accept (read-only).
* [application.service_views.StudioViews.build_approval](StudioViews.build_approval.md) - An unreviewed preview may run, but cannot inherit approval from a matching workflow alone.
* [application.service_views.StudioViews.edit_check](StudioViews.edit_check.md) - Dry-run one edit: {legal, codes, refs}.
* [application.service_views.StudioViews.export](StudioViews.export.md) - `def export(self, case_id: str) -> dict[str, Any]` in `application/service_views`.
* [application.service_views.StudioViews.formal_view](StudioViews.formal_view.md) - `def formal_view(self, model: Workflow) -> dict[str, Any]` in `application/service_views`.
* [application.service_views.StudioViews.history](StudioViews.history.md) - Reconstructed semantic revisions and append-only command audit; never changes the case.
* [application.service_views.StudioViews.repository_change](StudioViews.repository_change.md) - Compare immutable source revisions; this grants no model or repository write authority.
* [application.service_views.StudioViews.repository_change_file](StudioViews.repository_change_file.md) - Read bounded historical text and syntax; live source identity remains separate.
* [application.service_views.StudioViews.repository_freshness](StudioViews.repository_freshness.md) - Observe captured byte identity; this grants no source conformance, evidence or owner authority.
* [application.service_views.StudioViews.repository_impact](StudioViews.repository_impact.md) - Known repository links only.
* [application.service_views.StudioViews.repository_source](StudioViews.repository_source.md) - Bounded source view from the configured repository's captured nodes; no arbitrary path or execution.
* [application.service_views.StudioViews.view](StudioViews.view.md) - `def view(self, case_id: str, scope: str='local-demo') -> dict[str, Any]` in `application/service_views`.
* [application.service_views.StudioViews.workbench](StudioViews.workbench.md) - Current pack declarations and baseline, with separately labelled read-only repository facts.
* [application.service_views.StudioViews.workflows](StudioViews.workflows.md) - Baseline and candidate of a case, for read-only projections (diagrams).
