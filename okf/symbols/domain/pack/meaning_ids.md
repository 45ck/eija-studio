---
type: Function
title: domain.pack.meaning_ids
description: The meaning ids of the pack a workflow belongs to, or None when no such pack can be found.
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
  sha256: d5adef9a57103303edf01ecdcc07436c19161a0dcdf2279fb77fed22e0eec36c
notes_baseline: 44f03ddcbd2ed3e6660c9e8352870ee2f76efc43c635871a3fb76d2afd8da50a
---

# domain.pack.meaning_ids

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `def meaning_ids(pack_id: str, *, digest: str \| None=None) -> frozenset[str] \| None` |
| Code | `repo://src/eija_studio/domain/pack.py#meaning_ids` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The meaning ids of the pack a workflow belongs to, or None when no such pack can be found.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.pack.find_pack](/symbols/domain/pack/find_pack.md) - Resolve a loaded snapshot by digest, or an unambiguous id after refreshing its sources.
<!-- okf:generated:end links -->
