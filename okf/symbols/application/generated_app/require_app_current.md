---
type: Function
title: application.generated_app.require_app_current
description: A workflow-only historical case remains unbound; a bound app must still be current.
resource: repo://src/eija_studio/application/generated_app.py#require_app_current
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/generated_app.py#require_app_current
  title: application/generated_app.py
  hash_method: ast-v2
  sha256: c86e4dc07e28631eac5ef256eff52d4cb048d3918e8702fb61f0aca8c4ff943f
notes_baseline: 8e94259f6777ce5754d74bf975107cd3b2d6cd3d9b5877570945a957ac5084e9
---

# application.generated_app.require_app_current

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/generated_app`](/modules/application/generated_app.md) |
| Signature | `def require_app_current(case: ChangeCase, current: dict[str, Any] \| None) -> None` |
| Code | `repo://src/eija_studio/application/generated_app.py#require_app_current` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
A workflow-only historical case remains unbound; a bound app must still be current.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
<!-- okf:generated:end links -->
