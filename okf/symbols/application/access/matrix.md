---
type: Function
title: application.access.matrix
description: Every role's actions from every state, each tried in the kernel with the fixture actors in that role.
resource: repo://src/eija_studio/application/access.py#matrix
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/access.py#matrix
  title: application/access.py
  hash_method: ast-v2
  sha256: 24a434366a3ee306f5bbcc593d16d8a6405cd459709c812e668152b6e4b8d8a4
notes_baseline: 6df071434a07daaee5d76881905f251b31267b1eda54615402a036078355f6ea
---

# application.access.matrix

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/access`](/modules/application/access.md) |
| Signature | `def matrix(pack: Pack, model: Workflow) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/access.py#matrix` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Every role's actions from every state, each tried in the kernel with the fixture actors in that role.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.access.access](/symbols/application/access/access.md) - The matrix for `model`, and, when `base` differs, the permissions it adds, removes and changes compared with `base`.
<!-- okf:generated:end links -->
