---
type: Function
title: domain.pack.load_pack
description: Read current file contents and retain an immutable, digest-addressed pack snapshot.
resource: repo://src/eija_studio/domain/pack.py#load_pack
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#load_pack
  title: domain/pack.py
  hash_method: ast-v2
  sha256: 57f43f106ad9530ad34e8708153b447800fcea52ffda0d6de2e0747d3e0ef8f8
notes_baseline: e73fdaab5f02db62c63ffb01c6cfb771841f30e05b05346c88cea7c38122a52d
---

# domain.pack.load_pack

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `def load_pack(location: str \| Path, *, claim: bool=True) -> Pack` |
| Code | `repo://src/eija_studio/domain/pack.py#load_pack` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Read current file contents and retain an immutable, digest-addressed pack snapshot.

Files beside `pack.json` (data.json, screens.json, scenarios.json) are read from the folder the snapshot was read
from. Two folders can hold the same `pack.json` (a copy of a shipped pack whose class model was changed), so a
read that only looks at a pack, such as listing the templates or the workflows beside the open one, passes
`claim=False`: it does not move the snapshot to its folder, and the open system keeps reading its own files
(ADR-0250).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.pack.PACK_FILE](/symbols/domain/pack/PACK_FILE.md) - Constant `PACK_FILE` in `domain/pack`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [domain.pack.default_pack](/symbols/domain/pack/default_pack.md) - The configured pack, reread on every call and validated from a content-keyed cache.
<!-- okf:generated:end links -->
