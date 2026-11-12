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
  sha256: 65d959a21a42ba538cf81b5cbca12d98c11587ed0fcbf12d8440453cab83ac8e
notes_baseline: ecda8cfd92e2fa7a96689adc31b9d8b226f72311fd219c30db38ff3cde010e1d
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

* [application.access.access](/symbols/application/access/access.md) - The matrix for `model`, and, when `base` differs, the permissions it adds and removes compared with `base`.
<!-- okf:generated:end links -->
