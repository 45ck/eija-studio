---
type: Function
title: domain.pack.load_pack
description: Load a pack from a directory holding ``pack.json`` or from the file itself.
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
  sha256: 94b71b80701942229389f8544fba799b84e26b645b2c1cbb2a9132984022331c
notes_baseline: a86855176b86ad35125e4fd619ec25505b78264d9e2482037c0f69db58393055
---

# domain.pack.load_pack

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `def load_pack(location: str \| Path) -> Pack` |
| Code | `repo://src/eija_studio/domain/pack.py#load_pack` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Load a pack from a directory holding ``pack.json`` or from the file itself.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.pack.PACK_FILE](/symbols/domain/pack/PACK_FILE.md) - Constant `PACK_FILE` in `domain/pack`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.parse_pack](/symbols/domain/pack/parse_pack.md) - Validate a decoded JSON document as a pack.

## Referenced by

* [domain.pack.meaning_ids](/symbols/domain/pack/meaning_ids.md) - The meaning ids of the pack a workflow belongs to (``Workflow.id``): a pack loaded in this process, else the repository pack of that id.
<!-- okf:generated:end links -->
