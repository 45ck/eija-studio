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
  sha256: bfc2a3f6b917fc6a9c1e7c0a3bd73229083d1a00da37887edebfa56e2fce3042
notes_baseline: 5e563430cf19aa77ea00f47478770fbc7649137a5988d3e22641e87b19188f65
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
