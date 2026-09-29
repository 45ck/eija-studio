---
type: Function
title: domain.policy.declared_codes
description: Every transition must perform a declared action, with exactly its declared guards and required effects, and must declare every pack-forbidden effect forbidden.
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
  sha256: d01ed31dd8e9cf2ffe5d81355db1f38807deb9aabdaa162b61fa6eb03fb589fb
notes_baseline: 51627563ed892b7143231dfe9398c384e7d07641416e217a14b716b3be0ac190
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
Every transition must perform a declared action, with exactly its declared guards and required effects,
and must declare every pack-forbidden effect forbidden.
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
