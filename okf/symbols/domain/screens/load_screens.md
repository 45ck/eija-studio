---
type: Function
title: domain.screens.load_screens
description: The pack's screens, or None when the pack has no `screens.json`.
resource: repo://src/eija_studio/domain/screens.py#load_screens
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/screens.py#load_screens
  title: domain/screens.py
  hash_method: ast-v2
  sha256: b25dd5c2ef203564f1305f3222fc7589a00c90d21215d63a1bdc603d55614560
notes_baseline: 94bc1787d0208cc74aba526ece34f82680477f2d9b38bcade40823c1822bb49e
---

# domain.screens.load_screens

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/screens`](/modules/domain/screens.md) |
| Signature | `def load_screens(pack_directory: str \| Path, pack_id: str) -> Screens \| None` |
| Code | `repo://src/eija_studio/domain/screens.py#load_screens` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The pack's screens, or None when the pack has no `screens.json`.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.pack.pack_directory](/symbols/domain/pack/pack_directory.md) - The directory this exact pack snapshot was read from, or its authored directory, so optional files beside `pack.json` (such as `data.json`) are read from the s…
* [domain.screens.SCREENS_FILE](/symbols/domain/screens/SCREENS_FILE.md) - Constant `SCREENS_FILE` in `domain/screens`.
* [domain.screens.Screens](/symbols/domain/screens/Screens.md) - `class Screens(Contract)` in `domain/screens`.
* [domain.screens.parse_screens](/symbols/domain/screens/parse_screens.md) - `def parse_screens(document: Any, pack_id: str) -> Screens` in `domain/screens`.

## Referenced by

* [domain.screens.screens_for](/symbols/domain/screens/screens_for.md) - The screens beside this pack's `pack.json`, each use case they leave out given its default screen; or the defaults.
<!-- okf:generated:end links -->
