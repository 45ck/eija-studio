---
type: Method
title: application.service_views.StudioViews.workflows
description: Baseline and candidate of a case, for read-only projections (diagrams).
resource: repo://src/eija_studio/application/service_views.py#StudioViews.workflows
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service_views.py#StudioViews.workflows
  title: application/service_views.py
  hash_method: ast-v2
  sha256: 6bb8ca2d990c216719a397c3a67141caa15745a1ffb9c1b9805019466478350f
notes_baseline: e0d5b7c0a4be0bbfbb0276bda1038efba29b9bd19fa3f089454df18270f40bbe
---

# application.service_views.StudioViews.workflows

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service_views`](/modules/application/service_views.md) |
| Class | [`StudioViews`](/symbols/application/service_views/StudioViews.md) |
| Signature | `def workflows(self, case_id: str) -> tuple[Workflow, Workflow \| None]` |
| Code | `repo://src/eija_studio/application/service_views.py#StudioViews.workflows` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Baseline and candidate of a case, for read-only projections (diagrams). No authority, no writes.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
