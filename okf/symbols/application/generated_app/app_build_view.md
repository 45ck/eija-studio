---
type: Function
title: application.generated_app.app_build_view
description: Keep workflow evidence separate from generated application execution evidence.
resource: repo://src/eija_studio/application/generated_app.py#app_build_view
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/generated_app.py#app_build_view
  title: application/generated_app.py
  hash_method: ast-v2
  sha256: d3b3efc352fff6c3157c6c6a0f86e19be89e586a13454f645bfe4e1edc52eb85
notes_baseline: deac91d0cbb68e3744a23e6e01241d3fee85f38ae673f1dc90b41180b5f5d6de
---

# application.generated_app.app_build_view

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/generated_app`](/modules/application/generated_app.md) |
| Signature | `def app_build_view(case: ChangeCase, current: dict[str, Any] \| None, authentic: Callable[[dict[str, Any]], bool]) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/generated_app.py#app_build_view` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Keep workflow evidence separate from generated application execution evidence.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.
* [domain.evidence.combine](/symbols/domain/evidence/combine.md) - The status algebra: authenticated PASS and FAIL never average (CONFLICT); FAIL beats PASS-less states; STALE (a receipt for another subject), then NOT_RUN (a p…
* [domain.generated_app.generated_receipt_status](/symbols/domain/generated_app/generated_receipt_status.md) - Compute a scoped process observation, never trust its submitted status field.

## Referenced by

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],…` in `application/compiler`.
<!-- okf:generated:end links -->
