---
type: Function
title: domain.pack.derive
description: A draft of `pack` held in memory (`document`, checked as `parse_pack` checks any pack), whose files beside `pack.json` (`data.json`, `screens.json`, `scenarios.json`) are read from where `pack` was read.
resource: repo://src/eija_studio/domain/pack.py#derive
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#derive
  title: domain/pack.py
  hash_method: ast-v2
  sha256: ecf306a817f51d312b038c69f9c6b6e84c9b4e3abff1d0b218cfc9fd3eb62e0f
notes_baseline: 0d535fb13461cbb0e381cec28f967a121d371cfc2bf250183f9c0b1d4a2775a3
---

# domain.pack.derive

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `def derive(pack: Pack, document: Any) -> Pack` |
| Code | `repo://src/eija_studio/domain/pack.py#derive` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
A draft of `pack` held in memory (`document`, checked as `parse_pack` checks any pack), whose files beside
`pack.json` (`data.json`, `screens.json`, `scenarios.json`) are read from where `pack` was read. A draft is never a
loaded snapshot: `find_pack` cannot resolve it, so no change case or receipt can name it.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.pack_directory](/symbols/domain/pack/pack_directory.md) - The directory this exact pack snapshot was read from, or its authored directory, so optional files beside `pack.json` (such as `data.json`) are read from the s…
* [domain.pack.parse_pack](/symbols/domain/pack/parse_pack.md) - Validate a decoded JSON document as a pack.

## Referenced by

* [application.new_system.declare](/symbols/application/new_system/declare.md) - `pack` with every action and role `transactions` name but it does not declare yet, declared exactly as a sketch declares them (ADR-0201): an action gets the ba…
<!-- okf:generated:end links -->
