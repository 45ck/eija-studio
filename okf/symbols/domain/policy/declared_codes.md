---
type: Function
title: domain.policy.declared_codes
description: Every transition must perform a declared action, held by a declared role, with exactly its declared guards and required effects, and must declare every pack-forbidden effect forbidden.
resource: repo://src/eija_studio/domain/policy.py#declared_codes
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#declared_codes
  title: domain/policy.py
  hash_method: ast-v2
  sha256: 3841ffd1834df18ddffa9c1bbd60056e41a677eb6ea515383b2fab9ffce6c103
notes_baseline: c02b217f86e6780db6a0fb5066a6eb2643bef55b636d3ba7b2d098745b01c66a
---

# domain.policy.declared_codes

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def declared_codes(model: Workflow, pack: Pack) -> list[str]` |
| Code | `repo://src/eija_studio/domain/policy.py#declared_codes` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Every transition must perform a declared action, held by a declared role, with exactly its declared guards and
required effects, and must declare every pack-forbidden effect forbidden.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [domain.policy.check_policy](/symbols/domain/policy/check_policy.md) - Sorted, de-duplicated policy codes of ``model`` under the pack (empty means the model conforms).
<!-- okf:generated:end links -->
