---
type: Method
title: application.service_views.StudioViews.active_app_build
description: Read the atomically associated case and remeasure its exact approved generated application.
resource: repo://src/eija_studio/application/service_views.py#StudioViews.active_app_build
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service_views.py#StudioViews.active_app_build
  title: application/service_views.py
  hash_method: ast-v2
  sha256: cd8764e4a06f4a6590dbe523a2ff0be7175a02d1abce0c87a2355079ff5f7323
notes_baseline: 4ba949d23bae38d64c88c627dac9b5be77f23e0241b9ab8d1ad976b086cd75f3
---

# application.service_views.StudioViews.active_app_build

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service_views`](/modules/application/service_views.md) |
| Class | [`StudioViews`](/symbols/application/service_views/StudioViews.md) |
| Signature | `def active_app_build(self, active: dict[str, Any] \| None=None) -> dict[str, Any] \| None` |
| Code | `repo://src/eija_studio/application/service_views.py#StudioViews.active_app_build` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Read the atomically associated case and remeasure its exact approved generated application.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.generated_app.GeneratedAppActivation](/symbols/domain/generated_app/GeneratedAppActivation.md) - `class GeneratedAppActivation(Contract)` in `domain/generated_app`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
<!-- okf:generated:end links -->
