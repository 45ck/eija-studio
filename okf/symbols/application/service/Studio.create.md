---
type: Method
title: application.service.Studio.create
description: '`def create(self, request: str) -> dict[str, Any]` in `application/service`.'
resource: repo://src/eija_studio/application/service.py#Studio.create
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.create
  title: application/service.py
  hash_method: ast-v2
  sha256: a9e3120ff9f1099398641b6a21d73b1ee4d400cfd8e58d1e0cb0332c1fb25636
notes_baseline: 46f343ccdaad28ebf05ab5eba25a64d7e96597f5c0aa5e123fa9651cf87eba7c
---

# application.service.Studio.create

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def create(self, request: str) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service.py#Studio.create` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.service.now](/symbols/application/service/now.md) - `def now() -> str` in `application/service`.
* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models`.
<!-- okf:generated:end links -->
