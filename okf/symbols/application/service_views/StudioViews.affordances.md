---
type: Method
title: application.service_views.StudioViews.affordances
description: Which single edits of the case's working model the kernel would accept (read-only).
resource: repo://src/eija_studio/application/service_views.py#StudioViews.affordances
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service_views.py#StudioViews.affordances
  title: application/service_views.py
  hash_method: ast-v2
  sha256: 5077e6e32d2195b7bd8b7347efb32467b3d39538b7f62240e78b5568acada8a0
notes_baseline: 7bd34951237fbe4a873172268dd55510e4bca9e3ceb67c6d6fe5d8262758fc2b
---

# application.service_views.StudioViews.affordances

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service_views`](/modules/application/service_views.md) |
| Class | [`StudioViews`](/symbols/application/service_views/StudioViews.md) |
| Signature | `def affordances(self, case_id: str) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service_views.py#StudioViews.affordances` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Which single edits of the case's working model the kernel would accept (read-only).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.affordance.affordances](/symbols/domain/affordance/affordances.md) - Every single-step retarget and role change of ``model``, each with its dry-run verdict.
<!-- okf:generated:end links -->
