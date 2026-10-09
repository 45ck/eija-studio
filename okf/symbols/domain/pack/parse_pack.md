---
type: Function
title: domain.pack.parse_pack
description: Validate a decoded JSON document as a pack.
resource: repo://src/eija_studio/domain/pack.py#parse_pack
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#parse_pack
  title: domain/pack.py
  hash_method: ast-v2
  sha256: c69e071836979a3772f9b01a95aba8a03fbb046d9b9d68413ec41111fff02669
notes_baseline: 0697dd645d112084575fdd8f276b224684627970dd9fd412d14e0b040d4e22b2
---

# domain.pack.parse_pack

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `def parse_pack(document: Any) -> Pack` |
| Code | `repo://src/eija_studio/domain/pack.py#parse_pack` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Validate a decoded JSON document as a pack. Raises ``PackError`` with sorted diagnostics.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.PackError](/symbols/domain/pack/PackError.md) - A pack that cannot be used.
* [domain.pack.coherence_problems](/symbols/domain/pack/coherence_problems.md) - Every cross-reference defect of a structurally valid pack, sorted.

## Referenced by

* [application.law_proof.with_laws](/symbols/application/law_proof/with_laws.md) - The pack with its law file replaced by `laws` (a draft edited in PlayIDE), checked as the pack loader checks it.
* [application.new_system.summary](/symbols/application/new_system/summary.md) - What the new system has, for the form to say before it is created.
* [domain.pack.derive](/symbols/domain/pack/derive.md) - A draft of `pack` held in memory (`document`, checked as `parse_pack` checks any pack), whose files beside `pack.json` (`data.json`, `screens.json`, `scenarios…
<!-- okf:generated:end links -->
