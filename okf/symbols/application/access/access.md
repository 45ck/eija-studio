---
type: Function
title: application.access.access
description: The matrix for `model`, and, when `base` differs, the permissions it adds and removes compared with `base`.
resource: repo://src/eija_studio/application/access.py#access
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/access.py#access
  title: application/access.py
  hash_method: ast-v2
  sha256: 21d085000af09f19354258ef84964b175fe59a2d12de11a61fbdac06e659a316
notes_baseline: 3d439057ce2d1428f15a162f7d0c9abfe2a433685cbff8e23b39eee69018fbca
---

# application.access.access

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/access`](/modules/application/access.md) |
| Signature | `def access(pack: Pack, model: Workflow, base: Workflow \| None=None) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/access.py#access` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The matrix for `model`, and, when `base` differs, the permissions it adds and removes compared with `base`.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.access.matrix](/symbols/application/access/matrix.md) - Every role's actions from every state, each tried in the kernel with the fixture actors in that role.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
