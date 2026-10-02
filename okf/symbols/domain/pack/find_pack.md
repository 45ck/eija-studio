---
type: Function
title: domain.pack.find_pack
description: Resolve a loaded snapshot by digest, or an unambiguous id after refreshing its sources.
resource: repo://src/eija_studio/domain/pack.py#find_pack
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#find_pack
  title: domain/pack.py
  hash_method: ast-v2
  sha256: 0d37eb41617783b3185a9b001be1ebd7811066b8ed9f349b708a98e4cebd17e1
notes_baseline: 849b660bcbaf5d84a27537a9f1ed6d84cb404d1e744e1852a5bb181a4a63e327
---

# domain.pack.find_pack

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `def find_pack(pack_id: str, *, digest: str \| None=None) -> Pack \| None` |
| Code | `repo://src/eija_studio/domain/pack.py#find_pack` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Resolve a loaded snapshot by digest, or an unambiguous id after refreshing its sources.

An id alone cannot select between different observed contents, even when their model/version matches.
Ambiguity raises ``PACK_IDENTITY_REQUIRED`` rather than letting load order select policy or meanings.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.PackError](/symbols/domain/pack/PackError.md) - A pack that cannot be used.

## Referenced by

* [domain.pack.meaning_ids](/symbols/domain/pack/meaning_ids.md) - The meaning ids of the pack a workflow belongs to, or None when no such pack can be found.
<!-- okf:generated:end links -->
