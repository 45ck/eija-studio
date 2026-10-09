---
type: Function
title: application.screen_access.luminance
description: 'WCAG relative luminance of a #rrggbb colour.'
resource: repo://src/eija_studio/application/screen_access.py#luminance
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/screen_access.py#luminance
  title: application/screen_access.py
  hash_method: ast-v2
  sha256: 85c4569b023c5e77f2f76bc68a01a483deb5ecf553eb2aa7b4e227a79ef33c6d
notes_baseline: dc3aef0e9b34e5a380b5874dac8b1da9c51c1dcd3af0e2e333ecfbd3122987f9
---

# application.screen_access.luminance

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/screen_access`](/modules/application/screen_access.md) |
| Signature | `def luminance(colour: str) -> float` |
| Code | `repo://src/eija_studio/application/screen_access.py#luminance` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
WCAG relative luminance of a #rrggbb colour.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [application.screen_access.contrast](/symbols/application/screen_access/contrast.md) - `def contrast(foreground: str, background: str) -> float` in `application/screen_access`.
<!-- okf:generated:end links -->
