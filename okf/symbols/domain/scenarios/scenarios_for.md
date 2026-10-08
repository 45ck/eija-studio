---
type: Function
title: domain.scenarios.scenarios_for
description: The scenarios beside this pack's `pack.json`, or none.
resource: repo://src/eija_studio/domain/scenarios.py#scenarios_for
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/scenarios.py#scenarios_for
  title: domain/scenarios.py
  hash_method: ast-v2
  sha256: d2fde92ea87d23e2d325c0b6d5547803ca2bcf5a7b700326aa12e7ede3ae6589
notes_baseline: 3d8a9a7e1a5bfa6d318c6aff04ec9cd4e5c116cab15c16a2d41ac6102614d1f7
---

# domain.scenarios.scenarios_for

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/scenarios`](/modules/domain/scenarios.md) |
| Signature | `def scenarios_for(pack: Pack) -> Scenarios` |
| Code | `repo://src/eija_studio/domain/scenarios.py#scenarios_for` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The scenarios beside this pack's `pack.json`, or none.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.pack_directory](/symbols/domain/pack/pack_directory.md) - The directory this exact pack snapshot was read from, or its authored directory, so optional files beside `pack.json` (such as `data.json`) are read from the s…
* [domain.scenarios.Scenarios](/symbols/domain/scenarios/Scenarios.md) - `class Scenarios(Contract)` in `domain/scenarios`.
* [domain.scenarios.load_scenarios](/symbols/domain/scenarios/load_scenarios.md) - The scenarios in `directory`, or None when it has no `scenarios.json`.
<!-- okf:generated:end links -->
