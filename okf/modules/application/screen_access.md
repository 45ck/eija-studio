---
type: Module
title: application.screen_access
description: 'Accessibility of the generated screens (ADR-0218): what can be checked without a browser, checked every time.'
resource: repo://src/eija_studio/application/screen_access.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/screen_access.py
  title: application/screen_access.py
  hash_method: ast-api-v1
  sha256: 59c62dc8ee2965684863d3344caea1802929134dec95fcb4e8990f21b7b16cc5
notes_baseline: 1e5787355b01fa2bad6f449bf82ef5021fe83dc88dd370610a3e75938364e713
---

# application.screen_access

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/screen_access.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Accessibility of the generated screens (ADR-0218): what can be checked without a browser, checked every time.

The built app's page comes from fixed templates (`resources/appgen/web/`) filled with the designed screens and the
record class (ADR-0150, ADR-0154). So its accessibility has two parts. One is fixed by the templates: text contrast in
the light and the dark theme, colours that bypass the theme, labelled controls, keyboard order and how a required field
is marked. The other changes with every design: labels a screen repeats, labels that read as code, and actions from
one state that look alike. Both are judged here, against WCAG 2.2 level AA success criteria, with the measured value
where there is one. A pass is not a full audit: it says nothing about what only a person or a browser can judge (an
axe-core run on the built app is the browser tests' job).

Pure: the theme CSS and the page templates are passed in, so the same inputs always give the same report.
~~~

## Public symbols

* [`AA_TEXT`](/symbols/application/screen_access/AA_TEXT.md) (constant) - no docstring
* [`PAIRS`](/symbols/application/screen_access/PAIRS.md) (constant) - no docstring
* [`check_accessibility`](/symbols/application/screen_access/check_accessibility.md) (function) - Each check with its WCAG success criteria and PASS, WARN (advice) or FAIL, the design's first.
* [`contrast`](/symbols/application/screen_access/contrast.md) (function) - no docstring
* [`luminance`](/symbols/application/screen_access/luminance.md) (function) - WCAG relative luminance of a #rrggbb colour.
* [`themes`](/symbols/application/screen_access/themes.md) (function) - The theme tokens of the light page and of the dark one (the dark block overrides the light).

## Internal imports

* [`domain/data`](/modules/domain/data.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/screens`](/modules/domain/screens.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.data](/modules/domain/data.md) - The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.screens](/modules/domain/screens.md) - Screens: the user interface of a pack's app, designed against its use cases and data model (ADR-0154).

## Referenced by

* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
* [application.screen_access.AA_TEXT](/symbols/application/screen_access/AA_TEXT.md) - Constant `AA_TEXT` in `application/screen_access`.
* [application.screen_access.PAIRS](/symbols/application/screen_access/PAIRS.md) - Constant `PAIRS` in `application/screen_access`.
* [application.screen_access.check_accessibility](/symbols/application/screen_access/check_accessibility.md) - Each check with its WCAG success criteria and PASS, WARN (advice) or FAIL, the design's first.
* [application.screen_access.contrast](/symbols/application/screen_access/contrast.md) - `def contrast(foreground: str, background: str) -> float` in `application/screen_access`.
* [application.screen_access.luminance](/symbols/application/screen_access/luminance.md) - WCAG relative luminance of a #rrggbb colour.
* [application.screen_access.themes](/symbols/application/screen_access/themes.md) - The theme tokens of the light page and of the dark one (the dark block overrides the light).
<!-- okf:generated:end links -->
