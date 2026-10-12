---
type: Function
title: application.generated_app.app_build_blockers
description: '`def app_build_blockers(case: ChangeCase, view: dict[str, Any]) -> list[str]` in `application/generated_app`.'
resource: repo://src/eija_studio/application/generated_app.py#app_build_blockers
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/generated_app.py#app_build_blockers
  title: application/generated_app.py
  hash_method: ast-v2
  sha256: b621a204724d65dd064e77b67632850ff0fea49bcc1dc0307d357c1132511140
notes_baseline: 95b400d6b2211e47f40d8f4599ba383d16f91feaf926fb0d644083d8465e74fa
---

# application.generated_app.app_build_blockers

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/generated_app`](/modules/application/generated_app.md) |
| Signature | `def app_build_blockers(case: ChangeCase, view: dict[str, Any]) -> list[str]` |
| Code | `repo://src/eija_studio/application/generated_app.py#app_build_blockers` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.

## Referenced by

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],…` in `application/compiler`.
<!-- okf:generated:end links -->
