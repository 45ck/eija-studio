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
  sha256: b18e7b2b49f744e4034186c84a8b99285aa9a9fb473d88d28d9da69085dbbfc0
notes_baseline: c986c1d8c2e82f92a74ad077e640c5ada71996af70ac5cdf98f6a410a09f1b2d
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

One undeclared action and one unknown actor, both proven absent from this model and fixture directory, are the
negative controls for the missing-resolver refusals (ACTION_DENIED, UNKNOWN_ACTOR).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.appgen.UNDECLARED_ACTION](/symbols/application/appgen/UNDECLARED_ACTION.md) - Constant `UNDECLARED_ACTION` in `application/appgen`.
* [application.appgen.UNKNOWN_ACTOR](/symbols/application/appgen/UNKNOWN_ACTOR.md) - Constant `UNKNOWN_ACTOR` in `application/appgen`.
* [application.appgen.absent](/symbols/application/appgen/absent.md) - A name guaranteed not to be in `taken`, so a negative case can never collide with a declared one.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
<!-- okf:generated:end links -->
