---
type: Method
title: application.service_views.StudioViews.repository_change
description: Compare immutable source revisions; this grants no model or repository write authority.
resource: repo://src/eija_studio/application/service_views.py#StudioViews.repository_change
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service_views.py#StudioViews.repository_change
  title: application/service_views.py
  hash_method: ast-v2
  sha256: c0638113e74a2ea64934abe0831008a9bacb5b13ea8d5eafb92566ba671ff01c
notes_baseline: 150f7bcbd41d0ba212e44380c6659dbd1dae0c9bbb609c1619148c62a542fd63
---

# application.service_views.StudioViews.repository_change

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service_views`](/modules/application/service_views.md) |
| Class | [`StudioViews`](/symbols/application/service_views/StudioViews.md) |
| Signature | `def repository_change(self, base: str, head: str) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service_views.py#StudioViews.repository_change` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Compare immutable source revisions; this grants no model or repository write authority.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.repository.compare_repository_changes](/symbols/application/repository/compare_repository_changes.md) - Validate an immutable comparison request before dispatch to its read-only port.
<!-- okf:generated:end links -->
