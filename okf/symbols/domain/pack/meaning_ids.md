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
  sha256: 36bf9abd851ed642e51d9463e5322ee646947ad23f72ef77458296c92b869c95
notes_baseline: 7cb5565ca3342f1fc41ca8acd7edda9f97213dd25bf6dc1a2933b2bb5b12bf16
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
The meaning ids of the pack a workflow belongs to, or None when no such pack can be found.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.pack.find_pack](/symbols/domain/pack/find_pack.md) - The pack a workflow belongs to (``Workflow.id``): a pack loaded in this process, else the repository pack of that id.
<!-- okf:generated:end links -->
