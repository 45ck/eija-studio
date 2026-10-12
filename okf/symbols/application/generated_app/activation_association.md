---
type: Function
title: application.generated_app.activation_association
description: Exact-app provenance to be committed atomically with the active model by Studio.
resource: repo://src/eija_studio/application/generated_app.py#activation_association
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/generated_app.py#activation_association
  title: application/generated_app.py
  hash_method: ast-v2
  sha256: c320937b8c999042edbaa90a9e023f6132362bd5b3f1384191925bd45c0e7c30
notes_baseline: d43153a44a512c657fd312910919ee0a3478f7ccc79f8a48ae606adad96ac65f
---

# application.generated_app.activation_association

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/generated_app`](/modules/application/generated_app.md) |
| Signature | `def activation_association(case: ChangeCase, subject_hash: str) -> dict[str, Any] \| None` |
| Code | `repo://src/eija_studio/application/generated_app.py#activation_association` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Exact-app provenance to be committed atomically with the active model by Studio.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.

## Referenced by

* [application.service.Studio.apply](/symbols/application/service/Studio.apply.md) - `def apply(self, case_id: str, expected: int, principal: Principal) -> dict[str, Any]` in `application/service`.
<!-- okf:generated:end links -->
