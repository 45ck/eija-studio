---
type: Function
title: application.appgen.oracle_cases
description: Every state x action x actor x expected version, then the same request replayed.
resource: repo://src/eija_studio/application/appgen.py#oracle_cases
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/appgen.py#oracle_cases
  title: application/appgen.py
  hash_method: ast-v2
  sha256: a00962b9cd9d515652593fb12d4da4bdd0176464c93c9b20102da8aab74df8cb
notes_baseline: 556290fb5a65ae2bf8eeec4c6a32f15fb1deea1bfa1c604194a5e76dc2f39d40
---

# application.appgen.oracle_cases

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/appgen`](/modules/application/appgen.md) |
| Signature | `def oracle_cases(pack: Pack, model: Workflow) -> list[dict[str, Any]]` |
| Code | `repo://src/eija_studio/application/appgen.py#oracle_cases` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Every state x action x actor x expected version, then the same request replayed. The kernel answers each.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.appgen.UNDECLARED_ACTION](/symbols/application/appgen/UNDECLARED_ACTION.md) - Constant `UNDECLARED_ACTION` in `application/appgen`.
* [application.appgen.UNKNOWN_ACTOR](/symbols/application/appgen/UNKNOWN_ACTOR.md) - Constant `UNKNOWN_ACTOR` in `application/appgen`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
<!-- okf:generated:end links -->
