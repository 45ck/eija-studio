---
type: Method
title: application.service.Studio.create
description: '`def create(self, request: str) -> dict` in `application/service` (the source has no docstring).'
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
  hash_method: ast-v1
  sha256: 3b2fd74d4c565d5fe65a7727d81aae1309bfc639529df016ecd7f3c220ec3b54
---

# application.service.Studio.create

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def create(self, request: str) -> dict` |
| Code | `repo://src/eija_studio/application/service.py#Studio.create` |
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.service.now](/symbols/application/service/now.md) - `def now() -> str` in `application/service` (the source has no docstring).
* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models` (the source has no docstring).
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models` (the source has no docstring).
<!-- okf:generated:end links -->
