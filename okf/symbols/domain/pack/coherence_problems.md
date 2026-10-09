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
  sha256: 4b8d78bc8e02b514424a97690f3ad9b66696337a093746c565d046731fb0b689
notes_baseline: 4a703d3a8ef964dc5db222557fdc6e6570ee85d212d35bec1d0a0996c5bc003a
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
