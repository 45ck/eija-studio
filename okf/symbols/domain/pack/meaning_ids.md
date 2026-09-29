---
type: Function
title: domain.pack.meaning_ids
description: 'The meaning ids of the pack a workflow belongs to (``Workflow.id``): a pack loaded in this process, else the repository pack of that id.'
resource: repo://src/eija_studio/domain/pack.py#meaning_ids
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#meaning_ids
  title: domain/pack.py
  hash_method: ast-v2
  sha256: 5d511341d68767639fc4a9c9927c417d891af573de5a36d12c91e2d7e89a5f8c
notes_baseline: 1e3a48a9e2647e1f0306fb831cb43bcbfd8acf8cf3c3eac093c2ba4cb5482c8a
---

# domain.pack.meaning_ids

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `def meaning_ids(pack_id: str) -> frozenset[str] \| None` |
| Code | `repo://src/eija_studio/domain/pack.py#meaning_ids` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The meaning ids of the pack a workflow belongs to (``Workflow.id``): a pack loaded in this process, else the
repository pack of that id. None when no such pack can be found.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.pack.PACKS_ROOT](/symbols/domain/pack/PACKS_ROOT.md) - Constant `PACKS_ROOT` in `domain/pack`.
* [domain.pack.PACK_FILE](/symbols/domain/pack/PACK_FILE.md) - Constant `PACK_FILE` in `domain/pack`.
* [domain.pack.PACK_ID](/symbols/domain/pack/PACK_ID.md) - Constant `PACK_ID` in `domain/pack`.
* [domain.pack.PackError](/symbols/domain/pack/PackError.md) - A pack that cannot be used.
* [domain.pack.load_pack](/symbols/domain/pack/load_pack.md) - Load a pack from a directory holding ``pack.json`` or from the file itself.
<!-- okf:generated:end links -->
