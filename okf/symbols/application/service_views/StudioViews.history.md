---
type: Method
title: application.service_views.StudioViews.history
description: Reconstructed semantic revisions and append-only command audit; never changes the case.
resource: repo://src/eija_studio/application/service_views.py#StudioViews.history
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service_views.py#StudioViews.history
  title: application/service_views.py
  hash_method: ast-v2
  sha256: f587f1b29c077ea399bc40e04ffd0de7a56b391b097da6802cc5d3d8698c4d1b
notes_baseline: 87286b7b6f0dcd12fe6d6d22b9814b51800a3098d6a9b120da5552ea1d8738f1
---

# application.service_views.StudioViews.history

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service_views`](/modules/application/service_views.md) |
| Class | [`StudioViews`](/symbols/application/service_views/StudioViews.md) |
| Signature | `def history(self, case_id: str) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service_views.py#StudioViews.history` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Reconstructed semantic revisions and append-only command audit; never changes the case.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.history.history_view](/symbols/application/history/history_view.md) - Read-only models for navigation plus actual command audit entries; no invented legacy timestamps.
<!-- okf:generated:end links -->
