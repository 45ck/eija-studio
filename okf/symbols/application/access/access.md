---
type: Function
title: application.access.access
description: The matrix for `model`, and, when `base` differs, the permissions it adds, removes and changes compared with `base`.
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
  sha256: f1300c22c640d0b0b6e1c8cd81a1287b526873d4db931b68b0d9cb30019bc3b1
notes_baseline: a5cf8148da3a0c2a7e57348d49a6f099e15080b6045b30c7bde1e238641f1347
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
The matrix for `model`, and, when `base` differs, the permissions it adds, removes and changes compared with
`base`.
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
