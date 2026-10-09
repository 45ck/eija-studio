---
type: Function
title: application.screen_access.check_accessibility
description: Each check with its WCAG success criteria and PASS, WARN (advice) or FAIL, the design's first.
resource: repo://src/eija_studio/application/screen_access.py#check_accessibility
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/screen_access.py#check_accessibility
  title: application/screen_access.py
  hash_method: ast-v2
  sha256: 78a2eb8a95c6f14628de8d0c5899665513734a2e5cb49187f560a017b0c16b13
notes_baseline: c2701839af10b1bb1c223c369a38853a00a214bd6c7da4fcea963f52db8a234f
---

# application.screen_access.check_accessibility

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/screen_access`](/modules/application/screen_access.md) |
| Signature | `def check_accessibility(screens: Screens, model: Workflow, data: DataModel \| None, *, theme_css: str, page_js: str, page_html: str) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/screen_access.py#check_accessibility` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Each check with its WCAG success criteria and PASS, WARN (advice) or FAIL, the design's first.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.screens.Screens](/symbols/domain/screens/Screens.md) - `class Screens(Contract)` in `domain/screens`.
<!-- okf:generated:end links -->
