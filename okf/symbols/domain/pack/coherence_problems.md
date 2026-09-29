---
type: Function
title: domain.pack.coherence_problems
description: Every cross-reference defect of a structurally valid pack, sorted.
resource: repo://src/eija_studio/domain/pack.py#coherence_problems
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#coherence_problems
  title: domain/pack.py
  hash_method: ast-v2
  sha256: 0d2e2788980e1a71d54aa2a46c8c4800cbe8e4d4bc4d7fdc528539824332ba6a
notes_baseline: 27a2ca12f253ad7915b15aae54c51b2f2fd4cbf4e97b3d31326d7d00bdc11a6d
---

# domain.pack.coherence_problems

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `def coherence_problems(pack: Pack) -> list[str]` |
| Code | `repo://src/eija_studio/domain/pack.py#coherence_problems` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Every cross-reference defect of a structurally valid pack, sorted.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [domain.pack.parse_pack](/symbols/domain/pack/parse_pack.md) - Validate a decoded JSON document as a pack.
<!-- okf:generated:end links -->
