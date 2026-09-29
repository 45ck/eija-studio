---
type: Function
title: domain.policy.effects_table
description: Declared required effects per action.
resource: repo://src/eija_studio/domain/policy.py#effects_table
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#effects_table
  title: domain/policy.py
  hash_method: ast-v2
  sha256: cf566bbcb6f764d5939b275a184af0555b081b0eadc5ee86ab2189a77285c79c
notes_baseline: 5776ced06d329e1fcc8d6efb6e934eec2ab252a55fe9f914ce5472ef78aae800
---

# domain.policy.effects_table

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def effects_table(pack: Pack \| None=None) -> dict[str, tuple[str, ...]]` |
| Code | `repo://src/eija_studio/domain/policy.py#effects_table` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Declared required effects per action.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
