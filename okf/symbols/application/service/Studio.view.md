---
type: Method
title: application.service.Studio.view
description: '`def view(self, case_id: str, scope: str=''local-demo'') -> dict[str, Any]` in `application/service`.'
resource: repo://src/eija_studio/application/service.py#Studio.view
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.view
  title: application/service.py
  hash_method: ast-v2
  sha256: e0f2fdb900b2d82378e5cf9c7761033e5d61191e5a838490660c78e9fb004a7f
notes_baseline: 55d585bcc0f13138b0b6cf809d2cfa62cc69c803ad52148854e49acb63848acc
---

# application.service.Studio.view

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def view(self, case_id: str, scope: str='local-demo') -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service.py#Studio.view` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],…` in `application/compiler`.
* [domain.policy.CANONICAL_OPTIONS](/symbols/domain/policy/CANONICAL_OPTIONS.md) - Constant `CANONICAL_OPTIONS` in `domain/policy`.
<!-- okf:generated:end links -->
