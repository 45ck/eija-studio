---
type: Method
title: application.service_views.StudioViews.plan_check
description: Dry-run a whole plan of typed steps on the model in force, in order, as the chat's preview does (ADR-0230).
resource: repo://src/eija_studio/application/service_views.py#StudioViews.plan_check
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service_views.py#StudioViews.plan_check
  title: application/service_views.py
  hash_method: ast-v2
  sha256: b2204964b03e1ecc39779b1fa3dc8d5ef7ce7c01dafe9218828da527d3e4ef47
notes_baseline: 5c7d9cf878d3389ca87f71a7e900fa5bd10d815478e708c53d41bedab8847b30
---

# application.service_views.StudioViews.plan_check

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service_views`](/modules/application/service_views.md) |
| Class | [`StudioViews`](/symbols/application/service_views/StudioViews.md) |
| Signature | `def plan_check(self, steps: list[Any]) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service_views.py#StudioViews.plan_check` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Dry-run a whole plan of typed steps on the model in force, in order, as the chat's preview does (ADR-0230).
For a coding agent to ask "would the kernel accept this change?" before it writes code. Nothing is stored.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
