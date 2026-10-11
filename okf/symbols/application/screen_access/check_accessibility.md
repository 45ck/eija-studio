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
  sha256: a9cf4a5f2f2338cf6d5b4f428637e19695a9d22c84d9dc845cd0ec65682953b7
notes_baseline: dc4ca0456d9911284149caa0f2157a0bef6794f794d0957f0d1ea57639655f79
verified:
- by: process:playide-design
  at: '2026-10-11T01:03:14Z'
  notes_sha256: 2919302fdfa7f4858ab0b20e8722c7b6e12c5e6681d82d727eb6cec281671790
  sources_sha256: 39efe60f068a87c77b7ee9fc1fa00a64b16fe0e414f5b4a3ff1fea91f54d0662
- by: process:playide-integration
  at: '2026-10-11T06:19:22Z'
  notes_sha256: 2919302fdfa7f4858ab0b20e8722c7b6e12c5e6681d82d727eb6cec281671790
  sources_sha256: dc4ca0456d9911284149caa0f2157a0bef6794f794d0957f0d1ea57639655f79
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

The keyboard-order template check distinguishes signed literal indexes: `-1` is a programmatic focus target and `0` preserves sequential navigation; positive literal HTML/JavaScript indexes fail. Regression examples cover both accepted focus targets and reordered controls. This static check does not parse arbitrary JavaScript or establish actual focus behaviour; the generated-app browser journeys exercise cancellation, selection, refusals and outcome focus separately.

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.screens.Screens](/symbols/domain/screens/Screens.md) - `class Screens(Contract)` in `domain/screens`.
<!-- okf:generated:end links -->
