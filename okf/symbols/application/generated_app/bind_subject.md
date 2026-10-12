---
type: Function
title: application.generated_app.bind_subject
description: '`def bind_subject(subject: dict[str, Any], binding: GeneratedAppBinding | None) -> dict[str, Any]` in `application/generated_app`.'
resource: repo://src/eija_studio/application/generated_app.py#bind_subject
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/generated_app.py#bind_subject
  title: application/generated_app.py
  hash_method: ast-v2
  sha256: dfadb9e1c24088acbcec1f8a81b1ba16d84f4345c23494b3929070b98d6e32b4
notes_baseline: 832d1f0dd0b8c8f951987c09fc23c07307276df4529920aeeea6c2bc05665fae
---

# application.generated_app.bind_subject

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/generated_app`](/modules/application/generated_app.md) |
| Signature | `def bind_subject(subject: dict[str, Any], binding: GeneratedAppBinding \| None) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/generated_app.py#bind_subject` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.generated_app.GeneratedAppBinding](/symbols/domain/generated_app/GeneratedAppBinding.md) - `class GeneratedAppBinding(Contract)` in `domain/generated_app`.

## Referenced by

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],…` in `application/compiler`.
* [application.service.Studio.verify](/symbols/application/service/Studio.verify.md) - `def verify(self, case_id: str, expected: int) -> dict[str, Any]` in `application/service`.
<!-- okf:generated:end links -->
