---
type: Function
title: domain.pack.find_pack
description: 'The pack a workflow belongs to (``Workflow.id``): a pack loaded in this process, else the repository pack of that id.'
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
  sha256: 37f418cf9e59fd9bfbbc7f42b4125dba4b881949e8fb8fd3f3a02b817feb5c80
notes_baseline: e7da4f717edc5761e44e3c7659275ebdb5706e5f161acebd6b283d8f04e61484
---

# domain.pack.find_pack

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `def find_pack(pack_id: str) -> Pack \| None` |
| Code | `repo://src/eija_studio/domain/pack.py#find_pack` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The pack a workflow belongs to (``Workflow.id``): a pack loaded in this process, else the repository pack of
that id. None when no such pack can be found.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.pack.PACKS_ROOT](/symbols/domain/pack/PACKS_ROOT.md) - Constant `PACKS_ROOT` in `domain/pack`.
* [domain.pack.PACK_FILE](/symbols/domain/pack/PACK_FILE.md) - Constant `PACK_FILE` in `domain/pack`.
* [domain.pack.PACK_ID](/symbols/domain/pack/PACK_ID.md) - Constant `PACK_ID` in `domain/pack`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.PackError](/symbols/domain/pack/PackError.md) - A pack that cannot be used.
* [domain.pack.load_pack](/symbols/domain/pack/load_pack.md) - Load a pack from a directory holding ``pack.json`` or from the file itself.

## Referenced by

* [domain.pack.meaning_ids](/symbols/domain/pack/meaning_ids.md) - The meaning ids of the pack a workflow belongs to, or None when no such pack can be found.
<!-- okf:generated:end links -->
