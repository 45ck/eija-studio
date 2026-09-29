---
type: Function
title: domain.pack.state_sets
description: 'The state sets a workflow of this pack can have: the baseline''s, and the baseline''s after each supported meaning (states its transactions add or remove).'
resource: repo://src/eija_studio/domain/pack.py#state_sets
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#state_sets
  title: domain/pack.py
  hash_method: ast-v2
  sha256: 6b680dc958e60709fe1e8bd64e50a196186651065b610fe3dd299050a8985547
notes_baseline: 12891dcd54b69fb70651c6e54a9fcda5efd0e516781d9e86ff1a1d6c019f1272
---

# domain.pack.state_sets

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `def state_sets(pack: Pack) -> tuple[frozenset[str], ...]` |
| Code | `repo://src/eija_studio/domain/pack.py#state_sets` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The state sets a workflow of this pack can have: the baseline's, and the baseline's after each supported
meaning (states its transactions add or remove). Used to bound evidence whose model is not at hand.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [domain.evidence.expected_shape](/symbols/domain/evidence/expected_shape.md) - The runtime matrix a receipt must cover under ``pack``: exactly ``model``'s states when it is known.
<!-- okf:generated:end links -->
